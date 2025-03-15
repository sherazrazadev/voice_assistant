#  Voice Assistant - Flask Web App

Welcome to **Voice Assistant**, a Flask-based web application for voice-based interaction. This README provides a step-by-step guide to set up and run the application locally with HTTPS support for seamless voice conversation functionality.

---

## Requirements

- Python 3.9 or higher
- Virtual environment setup tools (optional but recommended)
- Ngrok for HTTPS tunneling

---

## Setup Instructions

### Step 1: Change to Project Directory
Move to the Project Directory using the command:

```bash
cd voice-assistant
```

---

### Step 2: Create a Virtual Environment
Create a virtual environment to manage dependencies:

```bash
python -m venv venv
```

Activate the virtual environment:

- On **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- On **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

---

### Step 3: Install Requirements
Install the required dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

---

### Step 4: Run the Flask App
Start the Flask app by running:

```bash
python app.py
```

The app will run on `http://127.0.0.1:5000` by default.

---

### Step 5: Enable HTTPS with Ngrok
To enable voice conversation functionality, HTTPS is required. Use Ngrok to create a secure tunnel:

1. Download and install Ngrok from [Ngrok Official Website](https://ngrok.com/).
2. Start the tunnel for the local Flask app by running:

   ```bash
   ngrok http 5000
   ```

3. Ngrok will generate a public HTTPS URL. Copy the URL and use it for voice-based interactions.

---

## Demo Link

For testing purposes, you can access the demo version of the  Voice Assistant using the following link:

---

## How to Use assistant

1. **Start a Conversation**  
   Open the application and click the **"Talk to assistant"** button to begin a voice conversation.

2. **Interrupting the Bot**  
   If you want to interrupt assistant during a conversation, simply say:

   **"Stop Emily"**

3. **Interaction Tips**  
   - Ensure you speak clearly for optimal voice recognition.
   - Use the HTTPS Ngrok URL if running the app locally for voice interactions.

---
