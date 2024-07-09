import os
import run
from flask_cors import CORS
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from flask import Flask, request, jsonify


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*", "supports_credentials": True, "max_age": 3600}})

@app.route('/chat', methods=['OPTIONS'])
def cors_handle():
    print(request.get_json())
        # Handle the preflight request here
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/chat', methods=['GET'])
def process_get():
    return jsonify({"YES":"YES YOU GET IT"})

@app.route('/chat', methods=['POST'])
def receive_message():
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'Missing "message" in request'}), 400

    system_message = \
    """
    You are a helpful bioinformatics classifier. You are helping me choose a
    useful tool for my client's task. There are 4 tool choices: (1) vulcan,
    (2) emu, (3) lemur, (4) none. You will only respons to messages with one word,
    either vulcan, emu, lemur, or none, depending on which tool the job is asking for
    (and if it is not asking for any tool, you will response with none).
    """

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
            max_tokens=5,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ])

        chatgpt_reply = response.choices[0].message.content

        if (chatgpt_reply in ["vulcan", "lemur", "emu"]):
            exit_code, dir = run.run_tool(chatgpt_reply)
            return jsonify({'response': f"You have asked for the execution of " \
                            f"{chatgpt_reply}. It was executed with exit code " \
                            f"{exit_code}.",
                            'path': dir})
        else:
            return continue_chat(user_message)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def continue_chat(user_message):
    system_message = \
    """
    You are a helpful bioinformatics assistant. Please respond briefly.
    """
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
            max_tokens=300,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ])

        chatgpt_reply = response.choices[0].message.content

        return jsonify({'response': chatgpt_reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
