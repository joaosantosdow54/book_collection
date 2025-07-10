from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('livros.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            num_livros INTEGER,
            valor_euros REAL,
            livros_faltantes INTEGER,
            total_livros INTEGER,
            preco_medio REAL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/books', methods=['GET'])
def get_books():
    conn = sqlite3.connect('livros.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livros")
    books = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': book[0],
        'nome': book[1],
        'num_livros': book[2],
        'valor_euros': book[3],
        'livros_faltantes': book[4],
        'total_livros': book[5],
        'preco_medio': book[6]
    } for book in books])

@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.json
    conn = sqlite3.connect('livros.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO livros (nome, num_livros, valor_euros, livros_faltantes,
                          total_livros, preco_medio)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['nome'],
        data['num_livros'],
        data['valor_euros'],
        data['livros_faltantes'],
        data['total_livros'],
        data['preco_medio']
    ))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Livro adicionado com sucesso!'})

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    conn = sqlite3.connect('livros.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE livros
        SET nome=?, num_livros=?, valor_euros=?, livros_faltantes=?,
            total_livros=?, preco_medio=?
        WHERE id=?
    ''', (
        data['nome'],
        data['num_livros'],
        data['valor_euros'],
        data['livros_faltantes'],
        data['total_livros'],
        data['preco_medio'],
        book_id
    ))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Livro atualizado com sucesso!'})

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = sqlite3.connect('livros.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM livros WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Livro excluído com sucesso!'})

@app.route('/api/books/import', methods=['POST'])
def import_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    try:
        df = pd.read_excel(file)
        conn = sqlite3.connect('livros.db')
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            try:
                values = (
                    str(row.get('NOME', '')),
                    int(float(row.get('Nº LIVROS', 0))),
                    float(row.get('VALOR(€)', 0.0)),
                    int(float(row.get('LIVROS EM FALTA', 0))),
                    int(float(row.get('TOTAL LIVROS', 0))),
                    float(row.get('PREÇO MÉDIO(€)', 0.0))
                )
                
                cursor.execute('''
                    INSERT INTO livros (
                        nome, num_livros, valor_euros, livros_faltantes,
                        total_livros, preco_medio
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', values)
            except Exception as e:
                print(f"Erro ao processar linha: {str(e)}")
                continue
        
        conn.commit()
        conn.close()
        return jsonify({'message': f'Importados {len(df)} registros com sucesso!'})
        
    except Exception as e:
        return jsonify({'error': f'Erro ao importar arquivo: {str(e)}'}), 500

@app.route('/api/summary')
def get_summary():
    conn = sqlite3.connect('livros.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            SUM(total_livros) as total_books,
            SUM(valor_euros) as total_value,
            AVG(preco_medio) as avg_price,
            SUM(livros_faltantes) as missing_books
        FROM livros
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({
        'total_books': result[0] or 0,
        'total_value': result[1] or 0,
        'avg_price': result[2] or 0,
        'missing_books': result[3] or 0
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True) 