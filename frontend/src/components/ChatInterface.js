import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';

const ChatInterface = ({ sessionId, onResumeGenerated }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [completed, setCompleted] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const addMessage = useCallback((sender, text) => {
        setMessages(prev => [...prev, { 
            sender, 
            text, 
            timestamp: new Date().toLocaleTimeString() 
        }]);
    }, []);

    const startSession = useCallback(async () => {
        try {
            setLoading(true);
            const response = await axios.post('http://localhost:8000/api/session', {
                user_id: null  // Send an empty object as required by the backend
            });
            addMessage('Bot', response.data.question);
        } catch (error) {
            console.error('Error starting session:', error);
            addMessage('Bot', 'Sorry, there was an error starting the conversation. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [addMessage]);

    const getCurrentQuestion = useCallback(async () => {
        try {
            setLoading(true);
            const response = await axios.post('http://localhost:8000/api/chat', {
                session_id: sessionId,
                message: ''
            });
            addMessage('Bot', response.data.question);
        } catch (error) {
            console.error('Error getting current question:', error);
            addMessage('Bot', 'Sorry, there was an error getting the current question. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [sessionId, addMessage]);

    useEffect(() => {
        // Start the conversation when component mounts
        if (!sessionId) {
            startSession();
        } else {
            // If we have a session ID, get the current question
            getCurrentQuestion();
        }
    }, [sessionId, startSession, getCurrentQuestion]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim() || loading) return;

        const userMessage = inputMessage;
        setInputMessage('');
        addMessage('You', userMessage);
        setLoading(true);

        try {
            const response = await axios.post('http://localhost:8000/api/chat', {
                session_id: sessionId,
                message: userMessage
            });

            addMessage('Bot', response.data.response);
            
            if (response.data.question) {
                addMessage('Bot', response.data.question);
            }

            if (response.data.completed) {
                setCompleted(true);
            }
            
            // If the response includes resume data, update the preview
            if (response.data.resume_data) {
                onResumeGenerated(response.data.resume_data);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage('Bot', 'Sorry, there was an error processing your message. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`flex ${
                            message.sender === 'You' ? 'justify-end' : 'justify-start'
                        }`}
                    >
                        <div
                            className={`max-w-[70%] rounded-lg p-3 ${
                                message.sender === 'You'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-200 text-gray-800'
                            }`}
                        >
                            <div className="font-semibold">{message.sender}</div>
                            <div className="whitespace-pre-wrap">{message.text}</div>
                            <div className="text-xs opacity-70 mt-1">
                                {message.timestamp}
                            </div>
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSendMessage} className="p-4 border-t">
                <div className="flex space-x-2">
                    <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        placeholder={completed ? "Type 'Generate my resume' to proceed" : "Type your answer..."}
                        className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className={`px-4 py-2 rounded-lg ${
                            loading
                                ? 'bg-gray-400 cursor-not-allowed'
                                : 'bg-blue-500 hover:bg-blue-600'
                        } text-white font-semibold`}
                    >
                        {loading ? 'Sending...' : 'Send'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ChatInterface; 