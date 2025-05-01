import aiohttp
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        self.base_url = "http://localhost:11434/api"
        self.model = "llama3"  # Using llama3 model

    async def generate_resume(self, user_data: Dict) -> str:
        """
        Generate a resume or chat response using the Ollama Llama3 model.
        
        Args:
            user_data: Dictionary containing user's information or chat context
            
        Returns:
            str: Generated response text
        """
        prompt = self._create_prompt(user_data)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {error_text}")
                        raise Exception(f"Ollama API error: {response.status}")
                    
                    result = await response.json()
                    return result["response"]
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def _create_prompt(self, user_data: Dict) -> str:
        """
        Create a prompt for the Ollama model based on user data.
        
        Args:
            user_data: Dictionary containing user's information or chat context
            
        Returns:
            str: Formatted prompt for the model
        """
        if "message" in user_data:
            # Chat message prompt
            messages = user_data.get("messages", [])
            context = "\n".join([f"{msg['text']}" for msg in messages[-5:]])  # Last 5 messages for context
            return f"""You are a helpful resume assistant. Based on the following conversation context, provide a helpful response:

Previous messages:
{context}

Current message: {user_data['message']}

Please provide a helpful response that guides the user in building their resume."""
        else:
            # Resume generation prompt
            return f"""Create a professional resume for {user_data.get('name', 'the candidate')} with the following information:

Name: {user_data.get('name', '')}
Title: {user_data.get('title', '')}
Summary: {user_data.get('summary', '')}

Education:
{self._format_education(user_data.get('education', []))}

Skills:
{', '.join(user_data.get('skills', []))}

Projects:
{self._format_projects(user_data.get('projects', []))}

Certifications:
{self._format_certifications(user_data.get('certifications', []))}

Languages:
{', '.join(user_data.get('languages', []))}

Please format the resume in markdown style with appropriate headings and sections.
Use bullet points for lists and maintain a professional tone throughout.
"""

    def _format_education(self, education: List[Dict]) -> str:
        return "\n".join([
            f"- {edu.get('institution', '')}, {edu.get('location', '')} - {edu.get('degree', '')} ({edu.get('year_range', '')})"
            for edu in education
        ])

    def _format_projects(self, projects: List[Dict]) -> str:
        return "\n".join([
            f"- {proj.get('name', '')}: {proj.get('description', '')}"
            for proj in projects
        ])

    def _format_certifications(self, certifications: List[Dict]) -> str:
        return "\n".join([
            f"- {cert.get('title', '')} - {cert.get('issuer', '')} ({cert.get('date', '')})"
            for cert in certifications
        ])

    async def enhance_resume(self, resume_data):
        try:
            # Prepare the prompt for enhancing the resume
            prompt = f"""You are a professional resume writer. Please enhance the following resume data to make it more professional and detailed.
            Keep the original information but expand upon it professionally.

            Original Resume Data:
            {json.dumps(resume_data, indent=2)}

            Please enhance the following sections:
            1. Summary: Make it more comprehensive and professional
            2. Skills: Add relevant technical and soft skills
            3. Projects: Add specific achievements and technologies used
            4. Experience: Add specific accomplishments and responsibilities
            5. Certifications: Add relevant details and achievements

            For example, if the input summary is "Web developer interest", enhance it to:
            "Highly motivated and detail-oriented web developer with expertise in HTML, CSS, and JavaScript. 
            Proficient in building responsive and user-friendly websites. Strong problem-solving skills and 
            a passion for creating efficient and scalable web applications."

            Return the enhanced data in the same JSON format. Only return the JSON, no additional text."""

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 2000
                        }
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        try:
                            # The response should be a JSON string
                            enhanced_data = json.loads(result["response"])
                            
                            # Ensure all required fields are present
                            for field in ['name', 'title', 'phone', 'email', 'location', 'summary', 
                                        'education', 'skills', 'projects', 'experience', 'certifications']:
                                if field not in enhanced_data:
                                    enhanced_data[field] = resume_data.get(field, '')
                            
                            # Log the enhanced data for debugging
                            logger.info(f"Enhanced resume data: {json.dumps(enhanced_data, indent=2)}")
                            
                            return enhanced_data
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse enhanced resume data: {str(e)}")
                            logger.error(f"Raw response: {result['response']}")
                            return resume_data
                    else:
                        error_text = await response.text()
                        logger.error(f"Error from Ollama API: {response.status} - {error_text}")
                        return resume_data

        except Exception as e:
            logger.error(f"Error enhancing resume: {str(e)}")
            return resume_data 