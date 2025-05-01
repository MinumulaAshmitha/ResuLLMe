import React from 'react';

const ResumePreview = ({ resumeData, sessionId }) => {
    if (!resumeData) return null;

    const handleDownload = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/download/${sessionId}`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `resume_${sessionId}.docx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Error downloading resume:', error);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Resume Preview</h2>
                <button
                    onClick={handleDownload}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                    Download DOCX
                </button>
            </div>

            <div className="space-y-6">
                {/* Header */}
                <div className="text-center">
                    <h1 className="text-3xl font-bold text-gray-900">{resumeData.name}</h1>
                    <p className="text-xl text-gray-600 mt-2">{resumeData.title}</p>
                </div>

                {/* Summary */}
                {resumeData.summary && (
                    <div>
                        <h2 className="text-xl font-semibold text-gray-800 mb-2">Summary</h2>
                        <p className="text-gray-700">{resumeData.summary}</p>
                    </div>
                )}

                {/* Education */}
                {resumeData.education && resumeData.education.length > 0 && (
                    <div>
                        <h2 className="text-xl font-semibold text-gray-800 mb-2">Education</h2>
                        <ul className="space-y-2">
                            {resumeData.education.map((edu, index) => (
                                <li key={index} className="text-gray-700">
                                    <strong>{edu.institution}</strong>
                                    {edu.location && `, ${edu.location}`}
                                    {edu.degree && ` - ${edu.degree}`}
                                    {edu.year_range && ` (${edu.year_range})`}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Skills */}
                {resumeData.skills && resumeData.skills.length > 0 && (
                    <div>
                        <h2 className="text-xl font-semibold text-gray-800 mb-2">Skills</h2>
                        <div className="flex flex-wrap gap-2">
                            {resumeData.skills.map((skill, index) => (
                                <span
                                    key={index}
                                    className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm"
                                >
                                    {skill}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* Projects */}
                {resumeData.projects && resumeData.projects.length > 0 && (
                    <div>
                        <h2 className="text-xl font-semibold text-gray-800 mb-2">Projects</h2>
                        <ul className="space-y-4">
                            {resumeData.projects.map((project, index) => (
                                <li key={index}>
                                    <h3 className="font-semibold text-gray-800">{project.name}</h3>
                                    <p className="text-gray-700">{project.description}</p>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Certifications */}
                {resumeData.certifications && resumeData.certifications.length > 0 && (
                    <div>
                        <h2 className="text-xl font-semibold text-gray-800 mb-2">Certifications</h2>
                        <ul className="space-y-2">
                            {resumeData.certifications.map((cert, index) => (
                                <li key={index} className="text-gray-700">
                                    <strong>{cert.title}</strong> - {cert.issuer} ({cert.date})
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Languages */}
                {resumeData.languages && resumeData.languages.length > 0 && (
                    <div>
                        <h2 className="text-xl font-semibold text-gray-800 mb-2">Languages</h2>
                        <div className="flex flex-wrap gap-2">
                            {resumeData.languages.map((language, index) => (
                                <span
                                    key={index}
                                    className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm"
                                >
                                    {language}
                                </span>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResumePreview; 