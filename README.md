# ResuLLMe - AI Chatbot-Based Resume Builder

ResuLLMe is a full-stack web application that enables users to generate professional resumes through an interactive, conversational interface. The system uses a React-based chat UI and a FastAPI backend that interacts with the Ollama (Gemma) AI model to process natural language prompts and generate resume content.

## Features

- Interactive chat interface for collecting resume details
- AI-powered resume content generation using Ollama (Gemma model)
- DOCX file generation with custom markdown-like formatting
- JSON schema parsing for structured data
- HTML preview of generated resumes
- Download functionality for DOCX files

## Technical Stack

### Frontend
- React.js
- HTML5 & CSS3
- Tailwind CSS (for styling)

### Backend
- FastAPI
- Python-docx
- Pydantic
- Ollama (Gemma model)
- Jinja2

## Prerequisites

- Python 3.8+
- Node.js 14+
- Ollama with Gemma model installed
- npm or yarn

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd resullme
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
cd backend
uvicorn main:app --reload
```

### 3. Frontend Setup
```bash
# Install dependencies
cd frontend
npm install

# Start the development server
npm start
```

### 4. Ollama Setup
Make sure you have Ollama installed and the Llama3 model downloaded:
```bash
ollama pull llama3:latest
```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Start a conversation with the chatbot by providing your resume details
3. The chatbot will guide you through collecting all necessary information
4. Once you're ready, type "generate my resume" or similar
5. Preview your resume and download it as a DOCX file

## API Endpoints

- `POST /api/session`: Start a new session
- `POST /api/chat`: Send a message to the chatbot
- `POST /api/generate`: Generate resume content
- `GET /api/resume_preview/{session_id}`: Get HTML preview of resume
- `GET /api/download/{session_id}`: Download resume as DOCX

## Project Structure

```
resullme/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── ollama_client.py     # Ollama API client
│   ├── resume_parser.py     # Markdown to JSON parser
│   ├── docx_generator.py    # DOCX file generator
│   ├── templates/           # Jinja2 templates
│   └── static/             # Static files
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.js         # Main application
│   │   └── index.js       # Entry point
│   ├── public/            # Public assets
│   └── package.json       # Frontend dependencies
├── requirements.txt       # Backend dependencies
└── README.md             # Project documentation
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

MIT License 