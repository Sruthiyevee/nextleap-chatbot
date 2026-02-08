# Phase 5: Web UI for NextLeap Chatbot

This phase provides a beautiful web interface for the NextLeap chatbot with a FastAPI backend and a modern HTML/CSS/JS frontend.

## 🏗️ Architecture

```
phase_5_ui/
├── backend/
│   ├── server.py          # FastAPI server
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── index.html         # Main UI
│   ├── styles.css         # Styling
│   └── script.js          # Frontend logic
└── run_chatbot.bat        # One-click launcher
```

## 🚀 Quick Start

### Option 1: One-Click Launch (Windows)
Simply double-click `run_chatbot.bat` to:
1. Install backend dependencies
2. Start the FastAPI server
3. Open the chatbot UI in your browser

### Option 2: Manual Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
python server.py
```

The API will be available at `http://localhost:8000`

#### Frontend
Open `frontend/index.html` in your browser.

## 📋 Prerequisites

- Python 3.8+
- GROQ API key (set in `../phase_4_llm/.env`)

## 🎨 Features

- **Modern UI**: Beautiful gradient design with smooth animations
- **Real-time Chat**: Instant responses from the chatbot
- **Typing Indicators**: Visual feedback while the bot is thinking
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: Graceful error messages if backend is down

## 🔧 API Endpoints

### `POST /chat`
Send a message to the chatbot.

**Request:**
```json
{
  "message": "What is the duration of the PM Fellowship?"
}
```

**Response:**
```json
{
  "response": "Great question! The Product Management Fellowship runs for 16 weeks..."
}
```

### `GET /health`
Check backend status.

**Response:**
```json
{
  "status": "ok",
  "llm_enabled": true
}
```

## 🎯 Usage

1. Run `run_chatbot.bat`
2. Wait for the browser to open
3. Start chatting with the NextLeap assistant!

Example queries:
- "What courses do you offer?"
- "Tell me about the Product Management Fellowship"
- "Who are the instructors?"
- "What is the cost of the UI/UX course?"

## 🛠️ Troubleshooting

**Backend not starting:**
- Ensure Python is installed and in PATH
- Check that all dependencies are installed: `pip install -r backend/requirements.txt`
- Verify GROQ_API_KEY is set in `../phase_4_llm/.env`

**Frontend not connecting:**
- Make sure the backend is running on `http://localhost:8000`
- Check browser console for errors
- Ensure CORS is enabled (already configured in `server.py`)

## 📝 Notes

- The frontend uses vanilla HTML/CSS/JS (no build step required)
- The backend reuses the retrieval engine from Phase 3
- All chatbot logic from Phase 4 is preserved
