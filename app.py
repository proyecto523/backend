from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route('/')
def get_productos():

    page = int(request.args.get('page', 1))
    per_page = 16
    offset = (page - 1) * per_page

    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM productos')
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT cantidad, nombre, precio_unitario
        FROM productos
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    productos = cursor.fetchall()
    conn.close()

    return {
        'productos': [
            {'cantidad': p[0], 'nombre': p[1], 'precio_unitario': p[2]}
            for p in productos
        ],
        'total': total,
        'page': page,
        'per_page': per_page
    }

def get_categorias():
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_categoría FROM categoría")
    categorias = cursor.fetchall()
    conn.close()
    return [
        {'categoria': p[0]}
        for p in categorias
    ]

@app.route('/api/productos')
def obtener_productos():
    return jsonify(get_productos())

@app.route('/api/categorias')
def obtener_categorias():
    return jsonify(get_categorias())

if __name__ == '__main__':
    app.run(debug=True)