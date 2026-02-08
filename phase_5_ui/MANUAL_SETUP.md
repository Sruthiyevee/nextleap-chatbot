# Manual Installation Guide for Phase 5

If the `run_chatbot.bat` file doesn't work, follow these manual steps:

## Step 1: Install Backend Dependencies

Open a terminal/command prompt and navigate to the backend folder:

```bash
cd phase_5_ui\backend
```

Install dependencies using one of these commands:

```bash
# Option 1: Using python -m pip (recommended)
python -m pip install -r requirements.txt

# Option 2: Using pip directly (if pip is in PATH)
pip install -r requirements.txt

# Option 3: Using py launcher (Windows)
py -m pip install -r requirements.txt
```

## Step 2: Start the Backend Server

In the same terminal, run:

```bash
python server.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!** The server needs to stay running.

## Step 3: Open the Frontend

Open a new File Explorer window and navigate to:
```
phase_5_ui\frontend\
```

Double-click `index.html` to open it in your default browser.

Alternatively, right-click `index.html` → Open with → Choose your preferred browser.

## Step 4: Start Chatting!

The chatbot UI should now be open in your browser and connected to the backend.

Try asking:
- "What courses do you offer?"
- "Tell me about the Product Management Fellowship"
- "Who are the instructors?"

## Troubleshooting

### "pip is not recognized"
- Use `python -m pip` instead of `pip`
- Or use `py -m pip` if you have the Python launcher

### "Python is not recognized"
- Install Python from https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

### Backend not starting
- Make sure you're in the `phase_5_ui\backend` folder
- Check that GROQ_API_KEY is set in `../../phase_4_llm/.env`

### Frontend shows "Backend not reachable"
- Make sure the backend server is running (Step 2)
- Check that it's running on http://localhost:8000
- Try refreshing the browser page

### Port 8000 already in use
Edit `server.py` and change the port:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change to 8001
```

Then update `frontend/script.js`:
```javascript
const API_URL = 'http://localhost:8001';  // Change to 8001
```

## Quick Reference

**Backend:**
```bash
cd phase_5_ui\backend
python -m pip install -r requirements.txt
python server.py
```

**Frontend:**
```bash
# Just open phase_5_ui\frontend\index.html in a browser
```
