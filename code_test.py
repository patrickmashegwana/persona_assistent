from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Float, Text, String
from sqlalchemy.exc import IntegrityError

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
