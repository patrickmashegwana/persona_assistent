import os

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
from sqlalchemy import Column, Integer, Float, Text, String
from sqlalchemy.exc import IntegrityError

# Load .env file
load_dotenv()

"""client = OpenAI()

response = client.responses.create(
    model="gpt-5-nano",
    input="Write a one-sentence bedtime story about a unicorn."
)
print(response.output_text)"""

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Persona(db.Model):
    __tablename__ = 'personas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    location = Column(Text, nullable=True)
    annual_income = Column(Float, nullable=True)
    extras = Column(Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'annual_income': self.annual_income,
            'extras': self.extras
        }


# Ensure DB and tables exist
with app.app_context():
    db.create_all()


# --- CRUD endpoints ---

@app.route('/personas', methods=['POST'])
def create_persona():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name is required'}), 400

    location = data.get('location')
    annual_income = data.get('annual_income')
    extras = data.get('extras')

    try:
        if annual_income is not None:
            try:
                annual_income = float(annual_income)
            except ValueError:
                return jsonify({'error': 'annual_income must be a number'}), 400

        persona = Persona(name=name, location=location, annual_income=annual_income, extras=extras)
        db.session.add(persona)
        db.session.commit()
        return jsonify(persona.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'database error'}), 500


@app.route('/personas', methods=['GET'])
def list_personas():
    personas = Persona.query.all()
    return jsonify([p.to_dict() for p in personas]), 200


@app.route('/personas/<int:persona_id>', methods=['GET'])
def get_persona(persona_id):
    p = Persona.query.get(persona_id)
    if not p:
        return jsonify({'error': 'not found'}), 404
    return jsonify(p.to_dict()), 200


@app.route('/personas/<int:persona_id>', methods=['PUT', 'PATCH'])
def update_persona(persona_id):
    p = Persona.query.get(persona_id)
    if not p:
        return jsonify({'error': 'not found'}), 404

    data = request.get_json() or {}
    name = data.get('name')
    if name is not None:
        p.name = name
    if 'location' in data:
        p.location = data.get('location')
    if 'annual_income' in data:
        ai = data.get('annual_income')
        if ai is not None:
            try:
                p.annual_income = float(ai)
            except ValueError:
                return jsonify({'error': 'annual_income must be a number'}), 400
        else:
            p.annual_income = None
    if 'extras' in data:
        p.extras = data.get('extras')

    db.session.commit()
    return jsonify(p.to_dict()), 200


@app.route('/personas/<int:persona_id>', methods=['DELETE'])
def delete_persona(persona_id):
    p = Persona.query.get(persona_id)
    if not p:
        return jsonify({'error': 'not found'}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'deleted'}), 200


# --- New endpoint: send persona + user message to OpenAI and return the AI response ---
@app.route('/personas/<int:persona_id>/prompt', methods=['POST'])
def persona_prompt(persona_id):
    """POST /personas/<id>/prompt
    Body JSON: {"message": "..."}

        The endpoint:
        - looks up the persona by id
        - builds a chat message that contains the persona details and the user's message
        - calls the OpenAI Chat Completions endpoint (expects OPENAI_API_KEY in env)
        - returns the AI's reply as JSON
"""
    data = request.get_json() or {}
    user_message = data.get('message')

    print(user_message)

    if not user_message:
        return jsonify({'error': 'message field is required in the request body'}), 400

    persona = Persona.query.get(persona_id)
    if not persona:
        return jsonify({'error': 'persona not found'}), 404

    # Build the system prompt with persona details
    persona_texts = [f"Name: {persona.name}"]
    if persona.location:
        persona_texts.append(f"Location: {persona.location}")
    if persona.annual_income is not None:
        persona_texts.append(f"Annual Income: {persona.annual_income}")
    if persona.extras:
        persona_texts.append(f"Extras: {persona.extras}")

    system_prompt = (
        "You are an assistant that should respond like the following persona. "
        "I will try to approach you for a sale of a product and you should respond based on your interest. "
        "Try to be realistic and don't say yes every time - you should only accept if you need the product. "
        "The following is the info for the persona that you are: "
        + ", ".join(persona_texts)
    )

    print(system_prompt)

    # Prepare messages for OpenAI chat endpoint
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        return jsonify({'error': 'OPENAI_API_KEY not set in environment'}), 500

    # Call OpenAI Chat Completions
    url = 'https://api.openai.com/v1/chat/completions'
    payload = {
        'model': 'gpt-5-mini',
        'messages': messages,
        'max_completion_tokens': 500
    }
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.RequestException as e:
        return jsonify({'error': 'failed to reach OpenAI API', 'details': str(e)}), 502

    if resp.status_code != 200:
        # forward error details from OpenAI
        try:
            return jsonify({'error': 'openai error', 'details': resp.json()}), resp.status_code
        except ValueError:
            return jsonify({'error': 'openai error', 'details': resp.text}), resp.status_code

    try:
        j = resp.json()
        ai_text = j['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({'error': 'unexpected OpenAI response', 'details': str(e), 'raw': resp.text}), 502

    return jsonify({'ai_response': ai_text}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
