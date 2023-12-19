from flask import Blueprint, render_template
from config.database import connect_to_database
from flask import Flask, Response, jsonify, request

articulo_fl1=Blueprint('articulo_id', __name__)

async def get_articulo(connection, id_articulo):
    try:
        async with connection.cursor() as cursor:
            sql_articulo = """
                SELECT a.*, 
                       e.id_especificacion, e.tipo, 
                       img.url_image, img.descripcion as img_descripcion
                FROM articulo a
                LEFT JOIN especificaciones e ON a.id_articulo = e.id_articulo
                LEFT JOIN images_articulo img ON a.id_articulo = img.id_articulo
                WHERE a.id_articulo = %s
            """
            await cursor.execute(sql_articulo, (id_articulo,))
            raw_results = await cursor.fetchall()

            if not raw_results:
                return None  # No se encontró el artículo

            articulo_resultado = {
                'id_articulo': raw_results[0]['id_articulo'],
                'marca': raw_results[0]['marca'],
                'modelo': raw_results[0]['modelo'],
                'categoria': raw_results[0]['categoria'],
                'ano': raw_results[0]['ano'],
                'precio': raw_results[0]['precio'],
                'kilometraje': raw_results[0]['kilometraje'],
                'created': int(raw_results[0]['created'].timestamp() * 1000),
                'lastUpdate': int(raw_results[0]['lastUpdate'].timestamp() * 1000),
                'lastInventoryUpdate':int(raw_results[0]['lastInventoryUpdate'].timestamp() * 1000),
                'enable': raw_results[0]['enable'],
                'descripcion': raw_results[0]['descripcion'],
                'enable': raw_results[0]['enable'],
                'color': raw_results[0]['color'],        
                'especificaciones': [],
                'imagenes': []
            }
            processed_especificaciones = set()
            for row in raw_results:
                id_especificacion = row.get('id_especificacion')

                if id_especificacion and id_especificacion not in processed_especificaciones:
                    processed_especificaciones.add(id_especificacion)

                    sql_subespecificaciones = """
                        SELECT * FROM subespecificaciones
                        WHERE id_especificacion = %s
                    """
                    await cursor.execute(sql_subespecificaciones, (id_especificacion,))
                    subespecificaciones_raw = await cursor.fetchall()
                    subespecificaciones = {sub['clave']: sub['valor'] for sub in subespecificaciones_raw}

                    especificacion = {
                        'tipo': row['tipo'],
                        'subespecificaciones': subespecificaciones
                    }
                    articulo_resultado['especificaciones'].append(especificacion)
                if row['url_image'] and not any(img['url_image'] == row['url_image'] for img in articulo_resultado['imagenes']):
                    imagen = {
                        'url_image': row['url_image'],
                        'descripcion': row['img_descripcion'],
                    }
                    articulo_resultado['imagenes'].append(imagen)

            return articulo_resultado
    finally:
        connection.close()

    
@articulo_fl1.route('/<int:articulo_id>', methods=['GET'])
async def get_articulo_by_id(articulo_id):
    async with connect_to_database() as con:
        try:
            articulo_by_id= await get_articulo(con,articulo_id)
            if articulo_by_id:
                return jsonify({"success": True, "data": articulo_by_id})
            else:
                return jsonify({"error": f"articulo with ID {articulo_id} not found"}), 404
        except Exception as e :
            return jsonify({"error":"Data Base erorr {}".format(e)})