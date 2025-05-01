import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChatInterface from './components/ChatInterface';
import ResumePreview from './components/ResumePreview';

function App() {
    const [sessionId, setSessionId] = useState('');
    const [resumeData, setResumeData] = useState(null);

    useEffect(() => {
        startNewSession();
    }, []);

    const startNewSession = async () => {
        try {
            const response = await axios.post('http://localhost:8000/api/session');
            setSessionId(response.data.session_id);
        } catch (error) {
            console.error('Error starting session:', error);
        }
    };

    const handleResumeGenerated = (data) => {
        setResumeData(data);
    };

    return (
        <div className="min-h-screen bg-gray-100">
            <div className="container mx-auto px-4 py-8">
                <header className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-800">ResuLLMe</h1>
                    <p className="text-xl text-gray-600 mt-2">AI-Powered Resume Builder</p>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="bg-white rounded-lg shadow-md overflow-hidden">
                        <div className="p-4 border-b">
                            <h2 className="text-xl font-semibold text-gray-800">Chat Interface</h2>
                            <p className="text-sm text-gray-600">Tell me about yourself to build your resume</p>
                        </div>
                        <ChatInterface
                            sessionId={sessionId}
                            onResumeGenerated={handleResumeGenerated}
                        />
                    </div>

                    <div className="bg-white rounded-lg shadow-md overflow-hidden">
                        <ResumePreview
                            resumeData={resumeData}
                            sessionId={sessionId}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App; 