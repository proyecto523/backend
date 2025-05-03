from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS

# Se crea la app Flask
app = Flask(__name__)
# Se habilita CORS para permitir peticiones desde el frontend (React u otros)
CORS(app)
@app.route('/')
# Función que obtiene productos desde la base de datos con paginación
def get_productos():
    # Se obtiene el número de página desde los parámetros de la URL (por defecto 1)
    page = int(request.args.get('page', 1))
    per_page = 16  # Cuántos productos mostrar por página
    offset = (page - 1) * per_page  # Cuántos registros saltar para esta página

    # Conexión a la base de datos SQLite
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()

    # Se consulta el total de productos en la base
    cursor.execute('SELECT COUNT(*) FROM productos')
    total = cursor.fetchone()[0]

    # Se obtienen los productos correspondientes a la página actual
    cursor.execute('''
        SELECT cantidad, nombre, precio_unitario, id_producto, descripción
        FROM productos
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    productos = cursor.fetchall()
    conn.close()

    # Se formatea y devuelve la información como un diccionario
    return {
        'productos': [
            {'cantidad': p[0], 'nombre': p[1], 'precio_unitario': p[2], 'id_producto': p[3], 'descripción':p[4]}
            for p in productos
        ],
        'total': total,
        'page': page,
        'per_page': per_page
    }

# Función que obtiene 12 productos desde la base de datos con paginación
@app.route('/api/productos15')
def obtener_productos_15():
    # Se obtiene el número de página desde los parámetros de la URL (por defecto 1)
    page = int(request.args.get('page', 1))
    per_page = 12  # Siempre se devuelven 12 productos por página
    offset = (page - 1) * per_page  # Cuántos registros saltar para esta página

    # Conexión a la base de datos SQLite
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()

    # Se consulta el total de productos en la base
    cursor.execute('SELECT COUNT(*) FROM productos')
    total = cursor.fetchone()[0]

    # Se obtienen los productos correspondientes a la página actual
    cursor.execute(''' 
        SELECT cantidad, nombre, precio_unitario, id_producto, descripción
        FROM productos
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    productos = cursor.fetchall()
    conn.close()

    # Se formatea y devuelve la información como un diccionario
    return {
        'productos': [
            {'cantidad': p[0], 'nombre': p[1], 'precio_unitario': p[2], 'id_producto': p[3], 'descripción': p[4]}
            for p in productos
        ],
        'total': total,
        'page': page,
        'per_page': per_page
    }


# Función que obtiene las categorías desde la base de datos
def get_categorias():
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_categoría FROM categoría")  # Consulta de categorías
    categorias = cursor.fetchall()
    conn.close()

    # Se transforma cada categoría en un diccionario
    return [
        {'categoria': p[0]}
        for p in categorias
    ]

# Ruta que devuelve los productos en formato JSON
@app.route('/api/productos')
def obtener_productos():
    return jsonify(get_productos())

# Ruta que devuelve las categorías en formato JSON
@app.route('/api/categorias')
def obtener_categorias():
    return jsonify(get_categorias())

# Hace que la app Flask se ejecute si este archivo se corre directamente
if __name__ == '__main__':
    app.run(debug=True)
