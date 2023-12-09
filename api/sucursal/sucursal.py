from flask import Blueprint, render_template
from config.database import connect_to_database
from flask import Flask, Response, jsonify, request


sucursal_fl = Blueprint('sucursal', __name__)


async def process_sucursal(connection):
    try:
        async with connection.cursor() as cursor:
            # Obtener registros de la tabla catalogo
            sql_sucursal = """SELECT id_sucursal, id_usuario,
              direccion, telefono, gerente, contacto, 
       correo_electronico, created, lastUpdate, url_logo,nombre,
         coordenadas,   
       horarios_de_atencion
    FROM sucursal;"""
            await cursor.execute(sql_sucursal)
            sucursal_results = await cursor.fetchall()
            # Procesar cada registro de sucursal
            for sucursal_record in sucursal_results:
                id_sucursal = sucursal_record['id_sucursal']

                # Obtener imágenes asociadas a la sucursal
                sql_sucursales = """SELECT * FROM images_sucursal
                                    WHERE id_sucursal = %s;"""
                await cursor.execute(sql_sucursales, (id_sucursal,))
                sucursal_images = await cursor.fetchall()

                # Obtener distribuidores asociados a la sucursal
                sql_distribuidor = """SELECT usuario.*
                                      FROM usuario
                                      JOIN distribuidor_sucursal ON usuario.id_usuario = distribuidor_sucursal.id_usuario
                                      WHERE usuario.rol = 'distribuidor' 
                                      AND distribuidor_sucursal.id_sucursal = %s;"""
                await cursor.execute(sql_distribuidor, (id_sucursal,))
                distribuidor_list = await cursor.fetchall()

                # Agregar la lista de imágenes y distribuidores como atributos adicionales
                sucursal_record['sucursal_images'] = sucursal_images
                sucursal_record['sucursal_distribuidores'] = distribuidor_list

            return sucursal_results
    finally:
        connection.close()


    
@sucursal_fl.route('/', methods=['GET'])
async def get_pedidos_proveedor():
    async with connect_to_database() as connection:
        try:
            # Obtener información de los pedidos del proveedor
            usuarios = await process_sucursal(connection)
            return jsonify({"success": True, "data": usuarios})
        except Exception as e:
            return jsonify({"error": "Database error: {}".format(e)}), 500