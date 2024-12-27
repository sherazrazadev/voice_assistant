from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import tempfile
import wave
import numpy as np
from gtts import gTTS
from faster_whisper import WhisperModel
from rag.AIVoiceAssistant import AIVoiceAssistant
from pydub import AudioSegment
from flask_cors import CORS


app = Flask(__name__)

# CORS configuration
CORS(app, resources={r"/*": {"origins": "*"}})

# Set up a folder for storing audio files
AUDIO_FOLDER = os.path.join(os.getcwd(), 'static', 'audio')
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

DEFAULT_MODEL_SIZE = "small"
DEFAULT_CHUNK_LENGTH = 10

# Initialize Whisper model once to reuse
model_size = DEFAULT_MODEL_SIZE + ".en"
model = WhisperModel(model_size, device="cpu", compute_type="int8", num_workers=10)

# Initialize AI Voice Assistant (assuming it's in your rag.AIVoiceAssistant)
ai_assistant = AIVoiceAssistant()
@app.route('/')
def index():
    output = "Welcome to Botmer International. I am Emily, how can I assist you today?"
    # generate_welcome_audio(output)  # Generate welcome message
    return render_template('index.html', welcome_message=output)
    
@app.route('/hello', methods=['GET'])
def hello():
    return "Hello, Botmer! Welcome to the platform."


@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    text = request.json.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    audio_path = os.path.join(AUDIO_FOLDER, 'welcome.mp3')
    tts = gTTS(text=text, lang='en')
    tts.save(audio_path)
    
    return jsonify({'audio_path': audio_path})
    
    
def generate_welcome_audio(text):
    welcome_audio_path = os.path.join(AUDIO_FOLDER, 'welcome.mp3')
    if not os.path.exists(welcome_audio_path):  # Avoid recreating
        tts = gTTS(text=text, lang='en')
        tts.save(welcome_audio_path)


def generate_speech_audio(text, speed=1.0):
    tts = gTTS(text=text, lang='en')
    
    temp_audio_file = f"temp_{next(tempfile._get_candidate_names())}.mp3"
    tts.save(temp_audio_file)
    audio = AudioSegment.from_file(temp_audio_file)
    if speed != 1.0:
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        }).set_frame_rate(audio.frame_rate)
    
    audio_filename = f"bot_response_{next(tempfile._get_candidate_names())}.mp3"
    audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
  
    audio.export(audio_path, format="mp3")
    os.remove(temp_audio_file)
    return f"https://api.botmer.io/static/audio/{audio_filename}"

def preprocess_text(text):
    """Format text into chat-friendly format."""
    
    # Remove newline characters
    text = text.replace('\n', ' ')

    # Remove any unwanted characters or redundant symbols like *, #, -
    cleaned_text = text.replace('*', '').replace('#', '').replace('-', '').strip()

    # Split text into sentences for better readability
    sentences = cleaned_text.split('. ')
    sentences = [sentence.capitalize().strip() for sentence in sentences if sentence]

    # Combine sentences into a single formatted response
    formatted_text = ' '.join(sentences)
    return formatted_text



# Handle audio file uploaded from client-side
@app.route('/record', methods=['POST'])
def record():
    try:
        # Check if the file is provided
        if 'audio' not in request.files:
            return jsonify({'response': "No audio file received."}), 400

        # Retrieve audio file
        audio_file = request.files['audio']
        audio_bytes = audio_file.read()

        # Save the file temporarily
        temp_file_path = 'temp_audio.wav'
        with open(temp_file_path, 'wb') as f:
            f.write(audio_bytes)

        # Transcribe audio using Whisper model
        transcription = transcribe_audio(temp_file_path)
        os.remove(temp_file_path)  # Remove temporary file after processing

        # Get AI Assistant response based on transcription
        bot_response = ai_assistant.interact_with_llm(transcription)
        
        if not bot_response:
            bot_response = "I couldn't understand that, please try again."
        bot_response = preprocess_text(bot_response)

        # Convert bot response to speech (TTS)
        audio_url = generate_speech_audio(bot_response, speed=1.1)

        # Return both transcription and the audio URL
        return jsonify({'response': bot_response, 'audio_url': audio_url})

    except Exception as e:
        return jsonify({'response': f"An error occurred: {str(e)}"}), 500

# Transcribe audio file using Whisper
def transcribe_audio(file_path):
    segments, info = model.transcribe(file_path, beam_size=7)
    transcription = ' '.join(segment.text for segment in segments)
    return transcription



user_sessions = {}

@app.route('/process', methods=['POST'])
def process_message():
    try:
        # Check if message and user_id are provided
        if 'message' not in request.json or 'user_id' not in request.json:
            return jsonify({'response': "No message or user_id received."}), 400

        user_message = request.json['message']
        user_id = request.json['user_id']

        # Retrieve previous conversation (if any)
        # previous_conversation = user_sessions.get(user_id, "")

        # Combine previous conversation with new message (optional)
        # combined_message = previous_conversation + " " + user_message

        # Get AI Assistant response
        bot_response = ai_assistant.interact_with_llm(user_message)

        # Save this conversation in the session for future reference
        user_sessions[user_id] = bot_response  # You could store more complex data

        if not bot_response:
            bot_response = "I couldn't understand that, please try again."

        bot_response = preprocess_text(bot_response)

        return jsonify({
            'reply': bot_response,
            'user_id': user_id
        })

    except Exception as e:
        return jsonify({'reply': f"An error occurred: {str(e)}"}), 500
        

@app.route('/text', methods=['POST'])
def text_input():
    try:
        # Check if text is provided in the request
        if 'text' not in request.json:
            return jsonify({'response': "No text provided."}), 400
        
        # Retrieve the text from the request
        user_input = request.json['text']

        # Get AI Assistant response based on the text input
        bot_response = ai_assistant.interact_with_llm(user_input)
        
        if not bot_response:
            bot_response = "I couldn't understand that, please try again."
        
        bot_response = preprocess_text(bot_response)


        # Return the bot's response and audio URL
        return jsonify({'response': bot_response})

    except Exception as e:
        return jsonify({'response': f"An error occurred: {str(e)}"}), 500
        
        
if __name__=="__main__":
          app.run(debug=True,port=5000,host="0.0.0.0")