import React, { useState, useRef, useEffect } from 'react';
import { PaperPlaneIcon } from '@radix-ui/react-icons';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const startNewSession = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to start session');
      }
      
      const data = await response.json();
      setSessionId(data.session_id);
      setMessages([{ role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Error starting session:', error);
      setMessages([{ 
        role: 'assistant', 
        content: "I apologize, but I encountered an error starting the session. Please try again." 
      }]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isGenerating) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsGenerating(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: input
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      
      // Only add the assistant's response if it's not empty
      if (data.response) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      }
      
      if (data.is_complete) {
        try {
          // Wait a moment to ensure the resume is generated
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          const downloadResponse = await fetch(`http://localhost:8000/api/download/${sessionId}`);
          if (!downloadResponse.ok) {
            throw new Error('Failed to download resume');
          }
          const blob = await downloadResponse.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'resume.docx';
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          
          // Start a new session after successful download
          startNewSession();
        } catch (error) {
          console.error('Error downloading resume:', error);
          setMessages(prev => [...prev, { 
            role: 'assistant', 
            content: "I apologize, but I encountered an error downloading your resume. Please try again." 
          }]);
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "I apologize, but I encountered an error. Please try again." 
      }]);
    } finally {
      setIsGenerating(false);
    }
  };

  // Initialize session when component mounts
  useEffect(() => {
    startNewSession();
  }, []);

  return (
    <Card className="w-full max-w-2xl mx-auto my-8 shadow-lg">
      <CardHeader className="bg-primary/5 border-b">
        <CardTitle className="text-xl font-semibold text-primary">ResuLLMe - Resume Builder</CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <ScrollArea className="h-[400px] mb-4 rounded-md border p-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`mb-4 flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                <p className="text-sm">{message.content}</p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </ScrollArea>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1"
            disabled={isGenerating}
          />
          <Button type="submit" disabled={isGenerating}>
            <PaperPlaneIcon className="h-4 w-4" />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default Chatbot; 