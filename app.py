from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
from werkzeug.security import check_password_hash  # Para verificar contraseñas

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])
@app.route('/')
# Función auxiliar para paginación de productos (versión principal)
def get_productos():
    page = int(request.args.get('page', 1))
    per_page = 16
    offset = (page - 1) * per_page

    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM productos')
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT cantidad, nombre, precio_unitario, id_producto, descripción
        FROM productos
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    productos = cursor.fetchall()
    conn.close()

    return {
        'productos': [
            {'cantidad': p[0], 'nombre': p[1], 'precio_unitario': p[2], 'id_producto': p[3], 'descripción': p[4]}
            for p in productos
        ],
        'total': total,
        'page': page,
        'per_page': per_page
    }

# Función auxiliar para obtener categorías
def get_categorias():
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id_categoría, nombre_categoría FROM categoría")
    categorias = cursor.fetchall()
    conn.close()
    return [{'id_categoría': c[0], 'categoria': c[1]} for c in categorias]


# Ruta para obtener productos (16 por página)
@app.route('/api/productos')
def obtener_productos():
    return jsonify(get_productos())

# Ruta para obtener productos (12 por página)
@app.route('/api/productos15')
def obtener_productos_15():
    page = int(request.args.get('page', 1))
    per_page = 12
    offset = (page - 1) * per_page

    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM productos')
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT cantidad, nombre, precio_unitario, id_producto, descripción
        FROM productos
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    productos = cursor.fetchall()
    conn.close()

    return jsonify({
        'productos': [
            {'cantidad': p[0], 'nombre': p[1], 'precio_unitario': p[2], 'id_producto': p[3], 'descripción': p[4]}
            for p in productos
        ],
        'total': total,
        'page': page,
        'per_page': per_page
    })

# Ruta para obtener categorías
@app.route('/api/categorias')
def obtener_categorias():
    return jsonify(get_categorias())

# Ruta para buscar productos
@app.route('/api/buscar', methods=['GET'])
def buscar_productos():
    termino = request.args.get('q', '').lower()
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT cantidad, nombre, precio_unitario, id_producto, descripción 
        FROM productos
        WHERE LOWER(nombre) LIKE ? OR LOWER(descripción) LIKE ?
    ''', (f'%{termino}%', f'%{termino}%'))
    resultados = cursor.fetchall()
    conn.close()
    return jsonify([
        {'cantidad': p[0], 'nombre': p[1], 'precio_unitario': p[2], 'id_producto': p[3], 'descripción': p[4]}
        for p in resultados
    ])

# Ruta para login de cliente/empleado
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    print("Datos recibidos:", data)
    usuario = data.get('usuario')
    password = data.get('password')
    is_empleado = data.get('isEmpleado')
    
    print(f"Usuario: {usuario}, Contraseña: {password}, ¿Empleado?: {is_empleado}")

    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    conn.row_factory = sqlite3.Row  # ← ESTO HACE LA MAGIA
    cursor = conn.cursor()

    if is_empleado:
        cursor.execute("SELECT * FROM empleado WHERE usuario = ?", (usuario,))
    else:
        cursor.execute("SELECT * FROM cliente WHERE usuario = ?", (usuario,))

    user = cursor.fetchone()

    if user:
        stored_password = user["contraseña"]  # ← AHORA usamos el NOMBRE de la columna
        if stored_password == password:
            return jsonify({"message": "Login exitoso"}), 200
        else:
            return jsonify({"error": "Contraseña incorrecta"}), 400
    else:
        return jsonify({"error": "Usuario no encontrado"}), 400

# Obtener cliente por ID
@app.route('/api/cliente/<int:id_cliente>', methods=['GET'])
def obtener_cliente(id_cliente):
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT id_cliente, nombre, apellido_pat, apellidos_mat, teléfono, email, usuario, contraseña 
        FROM cliente 
        WHERE id_cliente = ?
    ''', (id_cliente,))
    cliente = cursor.fetchone()
    conn.close()

    if cliente:
        return jsonify({
            'id_cliente': cliente[0],
            'nombre': cliente[1],
            'apellido_pat': cliente[2],
            'apellidos_mat': cliente[3],
            'teléfono': cliente[4],
            'email': cliente[5],
            'usuario': cliente[6],
            'contraseña': cliente[7]
        })
    else:
        return jsonify({'error': 'Cliente no encontrado'}), 404

# Agregar cliente
@app.route("/api/cliente", methods=["POST"])
def agregar_cliente():
    try:
        nombre = request.json.get('nombre')
        apellido_pat = request.json.get('apellido_pat')
        apellidos_mat = request.json.get('apellidos_mat')
        teléfono = request.json.get('teléfono')
        email = request.json.get('email')
        usuario = request.json.get('usuario')
        contraseña = request.json.get('contraseña')

        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(id_cliente) FROM cliente')
        ultimo_id = cursor.fetchone()[0]
        nuevo_id = ultimo_id + 1 if ultimo_id is not None else 1

        cursor.execute(''' 
            INSERT INTO cliente (id_cliente, nombre, apellido_pat, apellidos_mat, teléfono, email, usuario, contraseña)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nuevo_id, nombre, apellido_pat, apellidos_mat, teléfono, email, usuario, contraseña))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Cliente agregado exitosamente'}), 201

    except Exception as e:
        print(f"Error al agregar cliente: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

# Editar cliente
@app.route("/api/cliente/<int:id_cliente>", methods=["PUT"])
def editar_cliente(id_cliente):
    try:
        nombre = request.json.get('nombre')
        apellido_pat = request.json.get('apellido_pat')
        apellidos_mat = request.json.get('apellidos_mat')
        teléfono = request.json.get('teléfono')
        email = request.json.get('email')
        usuario = request.json.get('usuario')
        contraseña = request.json.get('contraseña')

        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE cliente
            SET nombre = ?, apellido_pat = ?, apellidos_mat = ?, teléfono = ?, email = ?, usuario = ?, contraseña = ?
            WHERE id_cliente = ?
        ''', (nombre, apellido_pat, apellidos_mat, teléfono, email, usuario, contraseña, id_cliente))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Cliente editado exitosamente'}), 200

    except Exception as e:
        print(f"Error al editar cliente: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


# Eliminar cliente
@app.route('/api/cliente/<int:id>', methods=['DELETE'])
def eliminar_cliente(id):
    try:
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cliente WHERE id_cliente = ?', (id,))
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({"message": "Cliente eliminado exitosamente"}), 200
        else:
            conn.close()
            return jsonify({"message": "Cliente no encontrado"}), 404
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error al eliminar el cliente: {str(e)}"}), 500

# Rutas adicionales para productos por categoría y filtrado por precio
@app.route('/api/productos/categoria_id/<int:id_categoria>')
def obtener_productos_por_categoria(id_categoria):
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT p.cantidad, p.nombre, p.precio_unitario, p.id_producto, p.descripción
        FROM "productos" p
        WHERE p."id_categoría" = ?
    ''', (id_categoria,))
    productos = cursor.fetchall()
    conn.close()
    return jsonify([
        {'cantidad': p[0], 'nombre': p[1], 'precio_unitario': p[2], 'id_producto': p[3], 'descripción': p[4]} 
        for p in productos
    ])

@app.route('/api/filtrar_por_precio')
def filtrar_por_precio():
    precio_min = request.args.get('min', type=float, default=0.0)
    precio_max = request.args.get('max', type=float)

    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    conn.row_factory = sqlite3.Row  # <- ESTO es lo que faltaba
    cursor = conn.cursor()

    if precio_max is not None:
        cursor.execute("SELECT * FROM productos WHERE precio_unitario BETWEEN ? AND ?", (precio_min, precio_max))
    else:
        cursor.execute("SELECT * FROM productos WHERE precio_unitario >= ?", (precio_min,))

    productos = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in productos])

# Obtener empleado por ID
@app.route('/api/empleado/<int:id_empleado>', methods=['GET'])
def obtener_empleado(id_empleado):
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT id_empleado, nombre, apellido_pat, apellidos_mat, cargo, usuario, contraseña
        FROM empleado 
        WHERE id_empleado = ?
    ''', (id_empleado,))
    empleado = cursor.fetchone()
    conn.close()

    if empleado:
        return jsonify({
            'id_empleado': empleado[0],
            'nombre': empleado[1],
            'apellido_pat': empleado[2],
            'apellidos_mat': empleado[3],
            'cargo': empleado[4],
            'usuario': empleado[5],
            'contraseña': empleado[6]
        })
    else:
        return jsonify({'error': 'Empleado no encontrado'}), 404

# Agregar empleado
@app.route("/api/empleado", methods=["POST"])
def agregar_empleado():
    try:
        data = request.get_json()
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(id_empleado) FROM empleado')
        ultimo_id = cursor.fetchone()[0]
        nuevo_id = ultimo_id + 1 if ultimo_id is not None else 1

        cursor.execute('''
            INSERT INTO empleado (id_empleado, nombre, apellido_pat, apellidos_mat, cargo, usuario, contraseña)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            nuevo_id, data['nombre'], data['apellido_pat'], data['apellidos_mat'],
            data['cargo'], data['usuario'], data['contraseña']
        ))

        conn.commit()
        conn.close()
        return jsonify({'message': 'Empleado agregado exitosamente'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Editar empleado
@app.route("/api/empleado/<int:id_empleado>", methods=["PUT"])
def editar_empleado(id_empleado):
    try:
        data = request.get_json()
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE empleado
            SET nombre = ?, apellido_pat = ?, apellidos_mat = ?, cargo = ?, usuario = ?, contraseña = ?
            WHERE id_empleado = ?
        ''', (
            data['nombre'], data['apellido_pat'], data['apellidos_mat'],
            data['cargo'], data['usuario'], data['contraseña'],
            id_empleado
        ))

        conn.commit()
        conn.close()
        return jsonify({'message': 'Empleado editado exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Eliminar empleado
@app.route('/api/empleado/<int:id_empleado>', methods=['DELETE'])
def eliminar_empleado(id_empleado):
    try:
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM empleado WHERE id_empleado = ?', (id_empleado,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Empleado eliminado exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Obtener producto por ID
@app.route('/api/producto/<int:id_producto>', methods=['GET'])
def obtener_producto(id_producto):
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT id_producto, id_categoría, nombre, descripción, precio_unitario, cantidad 
        FROM productos 
        WHERE id_producto = ?
    ''', (id_producto,))
    producto = cursor.fetchone()
    conn.close()

    if producto:
        return jsonify({
            'id_producto': producto[0],
            'id_categoría': producto[1],
            'nombre': producto[2],
            'descripción': producto[3],
            'precio_unitario': producto[4],
            'cantidad': producto[5]
        })
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404

# Agregar producto
@app.route("/api/producto", methods=["POST"])
def agregar_producto():
    try:
        data = request.get_json()
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO productos (id_producto, id_categoría, nombre, descripción, precio_unitario, cantidad)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['id_producto'], data['id_categoría'], data['nombre'], data['descripción'], 
            data['precio_unitario'], data['cantidad']
        ))

        conn.commit()
        conn.close()
        return jsonify({'message': 'Producto agregado exitosamente'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Editar producto
@app.route("/api/producto/<int:id_producto>", methods=["PUT"])
def editar_producto(id_producto):
    try:
        data = request.get_json()
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE productos
            SET id_categoría = ?, nombre = ?, descripción = ?, precio_unitario = ?, cantidad = ?
            WHERE id_producto = ?
        ''', (
            data['id_categoría'], data['nombre'], data['descripción'], 
            data['precio_unitario'], data['cantidad'], id_producto
        ))

        conn.commit()
        conn.close()
        return jsonify({'message': 'Producto editado exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Eliminar producto
@app.route('/api/producto/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    try:
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM productos WHERE id_producto = ?', (id_producto,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Producto eliminado exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Obtener proveedor por ID
@app.route('/api/proveedor/<int:id_proveedor>', methods=['GET'])
def obtener_proveedor(id_proveedor):
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT id_proveedor, nombre_empresa, teléfono, email, calle, número_ext, ciudad, estado, código_postal, país 
        FROM proveedor 
        WHERE id_proveedor = ?
    ''', (id_proveedor,))
    proveedor = cursor.fetchone()
    conn.close()

    if proveedor:
        return jsonify({
            'id_proveedor': proveedor[0],
            'nombre_empresa': proveedor[1],
            'teléfono': proveedor[2],
            'email': proveedor[3],
            'calle': proveedor[4],
            'número_ext': proveedor[5],
            'ciudad': proveedor[6],
            'estado': proveedor[7],
            'código_postal': proveedor[8],
            'país': proveedor[9]
        })
    else:
        return jsonify({'error': 'Proveedor no encontrado'}), 404

# Agregar proveedor
@app.route("/api/proveedor", methods=["POST"])
def agregar_proveedor():
    try:
        data = request.get_json()
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(id_proveedor) FROM proveedor')
        ultimo_id = cursor.fetchone()[0]
        nuevo_id = ultimo_id + 1 if ultimo_id is not None else 1

        cursor.execute('''
            INSERT INTO proveedor (
                id_proveedor, nombre_empresa, teléfono, email, calle, número_ext, ciudad, estado, código_postal, país
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nuevo_id, data['nombre_empresa'], data['teléfono'], data['email'],
            data['calle'], data['número_ext'], data['ciudad'], data['estado'],
            data['código_postal'], data['país']
        ))

        conn.commit()
        conn.close()
        return jsonify({'message': 'Proveedor agregado exitosamente'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Editar proveedor
@app.route("/api/proveedor/<int:id_proveedor>", methods=["PUT"])
def editar_proveedor(id_proveedor):
    try:
        data = request.get_json()
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE proveedor
            SET nombre_empresa = ?, teléfono = ?, email = ?, calle = ?, número_ext = ?, ciudad = ?, estado = ?, código_postal = ?, país = ?
            WHERE id_proveedor = ?
        ''', (
            data['nombre_empresa'], data['teléfono'], data['email'], data['calle'], data['número_ext'],
            data['ciudad'], data['estado'], data['código_postal'], data['país'], id_proveedor
        ))

        conn.commit()
        conn.close()
        return jsonify({'message': 'Proveedor editado exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Eliminar proveedor
@app.route('/api/proveedor/<int:id_proveedor>', methods=['DELETE'])
def eliminar_proveedor(id_proveedor):
    try:
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM proveedor WHERE id_proveedor = ?', (id_proveedor,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Proveedor eliminado exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Obtener compra por ID
@app.route('/api/compra/<int:id_compra>', methods=['GET'])
def obtener_compra(id_compra):
    conn = sqlite3.connect('BaseDatos-LLENADA.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT id_compra, id_proveedor, fecha, total
        FROM compra 
        WHERE id_compra = ?
    ''', (id_compra,))
    compra = cursor.fetchone()
    conn.close()

    if compra:
        return jsonify({
            'id_compra': compra[0],
            'id_proveedor': compra[1],
            'fecha': compra[2],
            'total': compra[3]
        })
    else:
        return jsonify({'error': 'Compra no encontrada'}), 404

# Agregar compra
@app.route("/api/compra", methods=["POST"])
def agregar_compra():
    try:
        data = request.get_json()
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(id_compra) FROM compra')
        ultimo_id = cursor.fetchone()[0]
        nuevo_id = ultimo_id + 1 if ultimo_id is not None else 1

        cursor.execute('''
            INSERT INTO compra (id_compra, id_proveedor, fecha, total)
            VALUES (?, ?, ?, ?)
        ''', (
            nuevo_id, data['id_proveedor'], data['fecha'], data['total']
        ))

        conn.commit()
        conn.close()
        return jsonify({'message': 'Compra agregada exitosamente'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Editar compra
@app.route("/api/compra/<int:id_compra>", methods=["PUT"])
def editar_compra(id_compra):
    try:
        data = request.get_json()
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE compra
            SET id_proveedor = ?, fecha = ?, total = ?
            WHERE id_compra = ?
        ''', (
            data['id_proveedor'], data['fecha'], data['total'], id_compra
        ))

        conn.commit()
        conn.close()
        return jsonify({'message': 'Compra editada exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Eliminar compra
@app.route('/api/compra/<int:id_compra>', methods=['DELETE'])
def eliminar_compra(id_compra):
    try:
        conn = sqlite3.connect('BaseDatos-LLENADA.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM compra WHERE id_compra = ?', (id_compra,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Compra eliminada exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ejecuta la app si este archivo se corre directamente
if __name__ == '__main__':
    app.run(debug=True)
