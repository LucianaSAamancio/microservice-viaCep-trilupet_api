from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from flasgger import Swagger 
import sqlite3

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

DB_NAME = "trilupet.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_nome TEXT NOT NULL,
            cep TEXT NOT NULL,
            logradouro TEXT,
            bairro TEXT,
            localidade TEXT,
            uf TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Rota principal redirecionando para a interface do Flasgger
@app.route('/')
def home():
    return redirect('/apidocs/')

# 1. ROTA GET (Listar agendamentos)
@app.route('/api/agendamentos', methods=['GET'])
def get_agendamentos():
    """
    Listar todos os agendamentos
    ---
    responses:
      200:
        description: Lista de agendamentos cadastrados
        schema:
          type: array
          items:
            properties:
              id:
                type: integer
                example: 1
              pet_nome:
                type: string
                example: "Rex"
              cep:
                type: string
                example: "21221-000"
              logradouro:
                type: string
                example: "Rua Exemplo"
              bairro:
                type: string
                example: "Centro"
              localidade:
                type: string
                example: "Rio de Janeiro"
              uf:
                type: string
                example: "RJ"
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM agendamentos')
    rows = cursor.fetchall()
    conn.close()
    
    agendamentos = []
    for row in rows:
        agendamentos.append({
            "id": row[0],
            "pet_nome": row[1],
            "cep": row[2],
            "logradouro": row[3],
            "bairro": row[4],
            "localidade": row[5],
            "uf": row[6]
        })
    return jsonify(agendamentos), 200

# 2. ROTA POST (Criar agendamento com dados de endereço obtidos via ViaCEP)
@app.route('/api/agendamentos', methods=['POST'])
def create_agendamento():
    """
    Criar novo agendamento
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - pet_nome
            - cep
          properties:
            pet_nome:
              type: string
              example: "Rex"
            cep:
              type: string
              example: "21221-000"
            logradouro:
              type: string
              example: "Rua Exemplo"
            bairro:
              type: string
              example: "Centro"
            localidade:
              type: string
              example: "Rio de Janeiro"
            uf:
              type: string
              example: "RJ"
    responses:
      201:
        description: Agendamento criado com sucesso
        schema:
          properties:
            id:
              type: integer
              example: 1
            message:
              type: string
              example: "Agendamento criado com sucesso!"
      400:
        description: Campos 'pet_nome' e 'cep' são obrigatórios.
        schema:
          properties:
            error:
              type: string
              example: "Campos 'pet_nome' e 'cep' são obrigatórios."
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Corpo da requisição inválido ou ausente."}), 400

    pet_nome = data.get('pet_nome')
    cep = data.get('cep')
    logradouro = data.get('logradouro', '')
    bairro = data.get('bairro', '')
    localidade = data.get('localidade', '')
    uf = data.get('uf', '')
    
    if not pet_nome or not cep:
        return jsonify({"error": "Campos 'pet_nome' e 'cep' são obrigatórios."}), 400
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO agendamentos (pet_nome, cep, logradouro, bairro, localidade, uf)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (pet_nome, cep, logradouro, bairro, localidade, uf))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": new_id, "message": "Agendamento criado com sucesso!"}), 201

# 3. ROTA PUT (Atualizar agendamento existente)
@app.route('/api/agendamentos/<int:id>', methods=['PUT'])
def update_agendamento(id):
    """
    Atualizar agendamento
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do agendamento
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            pet_nome:
              type: string
              example: "Thor"
    responses:
      200:
        description: Agendamento atualizado com sucesso
        schema:
          properties:
            message:
              type: string
              example: "Agendamento atualizado com sucesso!"
      404:
        description: Agendamento não encontrado
        schema:
          properties:
            error:
              type: string
              example: "Agendamento não encontrado."
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Corpo da requisição inválido ou ausente."}), 400

    pet_nome = data.get('pet_nome')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE agendamentos SET pet_nome = ? WHERE id = ?', (pet_nome, id))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return jsonify({"error": "Agendamento não encontrado."}), 404
    return jsonify({"message": "Agendamento atualizado com sucesso!"}), 200

# 4. ROTA DELETE (Remover agendamento)
@app.route('/api/agendamentos/<int:id>', methods=['DELETE'])
def delete_agendamento(id):
    """
    Remover agendamento
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do agendamento a ser removido
    responses:
      200:
        description: Agendamento removido com sucesso
        schema:
          properties:
            message:
              type: string
              example: "Agendamento removido com sucesso!"
      404:
        description: Agendamento não encontrado
        schema:
          properties:
            error:
              type: string
              example: "Agendamento não encontrado."
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM agendamentos WHERE id = ?', (id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Agendamento não encontrado."}), 404
    return jsonify({"message": "Agendamento removido com sucesso!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)