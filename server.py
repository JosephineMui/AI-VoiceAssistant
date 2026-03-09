import base64
import json
from flask import Flask, render_template, request
from worker import speech_to_text, text_to_speech, openai_process_message
from flask_cors import CORS
import os

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_route():
    print("processing speech-to-text")

    audio_binary = request.data # Get the user's speech from request
    text = speech_to_text(audio_binary)

    # Return the response back to the user in JSON format
    # Use the Flask's app.response_class function to create the response
    # response=json.dumps is the actual data sent in the body of our HTTP response
    response = app.response_class(
        response=json.dumps({'text': text}),
        status=200,
        mimetype='application/json'
    )

    print(response)
    print(response.data)
    return response


@app.route('/process-message', methods=['POST'])
def process_prompt_route():
    user_message = request.json['userMessage']
    print('user_message', user_message)

    voice = request.json['voice']
    print('voice', voice)

    response_text = openai_process_message(user_message)

    # Clean the response to remove any empty lines
    response_text = os.linesep.join([s for s in response_text.splitlines() if s])

    # Call text_to_speech to convert OpenAI Api's response to speech
    response_speech = text_to_speech(response_text, voice)

    # Convert sppech to base64 string so it can be sent back in JSON response
    '''
    As the openai_response_speech is a type of audio data, we can't directly 
    send this inside a json as it can only store textual data. Therefore, we 
    will be using something called "base64 encoding". In simple words, we can 
    convert any type of binary data to a textual representation by encoding 
    the data in base64 format. 
    '''
    response_speech = base64.b64encode(response_speech).decode('utf-8')

	# Send a JSON response back to the user containing their message's response both in text 
    # and speech formats
    response = app.response_class(
        response=json.dumps({"openaiResponseText": response_text, "openaiResponseSpeech": response_speech}),
        status=200,
        mimetype='application/json'
    )

    print(response)
    return response


if __name__ == "__main__":
    app.run(port=8000, host='0.0.0.0')
