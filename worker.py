from openai import OpenAI
import requests

openai_client = OpenAI()


def speech_to_text(audio_binary):

    # Set up Watson Speech-to-Text HTTP Api url
    base_url = "https://sn-watson-stt.labs.skills.network"
    api_url = base_url + '/speech-to-text/api/v1/recognize'

    # Set up parameters for our HTTP request
    # Tells Watson to use the US English model for processing the speech
    params = {
        'model': 'en-US_Multimedia',
    }

    # Send a HTTP Post request
    response = requests.post(api_url, params=params, data=audio_binary).json()

    '''
    Structure of the response:

    {
        "response": {
            "results": {
                "alternatives": {
                    "transcript": "Recognised text from your speech"
                }
            }
        }
    }   
    '''

    # Parse the response to get the transcribed text
    text = 'null'
    while bool(response.get('results')):
        print('speech to text response:', response)
        # pop() is used to get the last item in the list and remove it from the list. 
        # We use it here to get the most recent transcription result.
        text = response.get('results').pop().get('alternatives').pop().get('transcript')
        print('recognized text: ', text)
        return text


def text_to_speech(text, voice=""):
    base_url = "https://sn-watson-tts.labs.skills.network"
    api_url = base_url + "/text-to-speech/api/v1/synthesize?output=output_text.wav"

    # Adding voice parameter in api_url if the user has selected a preferred voice
    if voice != "" and voice != "default":
        api_url += "&voice=" + voice

    # Set the headers for HTTP request
    # "Accept": "audio/wav" => sending an audio wav format
    # "Content-Type": application/json" => format of the body is JSON
    headers = {
        "Accept": "audio/wav",
        "Content-Type": "application/json",
    }

    # Set the body of HTTP request
    json_data = { "text": text }

    # Send HTTP Post request
    response = requests.post(api_url, headers=headers, json=json_data)

    '''
    Structure of the response:

    {
        "response": {
                content: The Audio data for the processed text to speech
            }
        }
    }
    '''
    print("text to speech response:", response)

    return response.content


def openai_process_message(user_message):

    # Set the prompt for OpenAI Api
    # Tell the model to become a personal assistant.
    # Giving it specific tasks
    # By adding the original user message afterwards, it gives OpenAI more
    # room to sound genuine.
    prompt = "Act like a personal assistant. You can respond to questions, translate sentences, summarize news, and give recommendations. Keep responses concise - 2 to 3 sentences maximum."

    client = OpenAI()

    # Call the OpenAI Api to process our prompt
    '''
    The messages parameter is an array of objects used to define the conversation
    flow between the user and the AI. Each object represents a message with two key
    attributes: role (identifying the sender as either "system" for setup instructions
    or "user" for the actual user query) and content (the message text).
    
    The "system" role message instructs the AI on how to behave (for example, acting
    like a personal assistant), while the "user" role message contains the user's input.
    This structured approach helps tailor the AI's responses to be more relevant and
    personalized.
    '''
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ],
        max_completion_tokens=1000
    )

    '''
    Structure of the response:

    {
        "choices": [
                {"message": {
                    content: "The model\'s answer to our prompt",
                    ...,
                    ...,
                },
                ...,
                ...
            ]
    }
   
    '''
    print("openai response:", response)

    # Parse the response to get the message
    response_text = response.choices[0].message.content

    return response_text
