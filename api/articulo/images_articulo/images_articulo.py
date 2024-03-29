from flask import Blueprint, request, jsonify
from config.database import connect_to_database

articulo_fl3 = Blueprint('articulo_fl3', __name__)

@articulo_fl3.route('/imagen_articulo', methods=['POST'])
def insertar_imagen_articulo():
    try:
        with connect_to_database() as connection:
            data = request.json
            campos_requeridos = ['url_image', 'descripcion', 'id_articulo']

            if not all(campo in data for campo in campos_requeridos):
                return jsonify({"error": "Faltan campos requeridos"}), 400

            with connection.cursor() as cursor:
                sql = """INSERT INTO images_articulo (url_image, descripcion, id_articulo) 
                         VALUES (?, ?, ?)"""
                valores = (data['url_image'], data['descripcion'], data['id_articulo'])

                cursor.execute(sql, valores)
                connection.commit()

            return jsonify({"success": True, "message": "Imagen de artículo insertada exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
