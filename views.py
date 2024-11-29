from json import dumps
from bson import ObjectId
from flask import Blueprint, json, jsonify, render_template, request
from db import collection


views = Blueprint(__name__, 'views')

@views.route('/home')
def home():
    return render_template('index.html')


@views.route('/crear_institucion', methods=['GET'])
def create_institucion_form():
    return render_template('crear.html')

@views.route('/add', methods=['POST'])
def add_document():
    try:
        # Get the form data from the request
        title = request.form.get("title")
        content = request.form.get("content")
        author = request.form.get("author", "Anonymous")

        # Get course data
        courses = []
        for i in range(10):  # Limit to 10 courses for simplicity
            course_name = request.form.get(f"courses[{i}][name]")
            if not course_name:
                continue
            students = request.form.getlist(f"courses[{i}][students][]")
            courses.append({
                "name": course_name,
                "students": students
            })

        # Validate required fields
        if not title or not content or not courses:
            return jsonify({"error": "Missing required fields"}), 400

        # Insert into MongoDB collection
        result = collection.insert_one({
            "title": title,
            "content": content,
            "author": author,
            "courses": courses,  # Store courses as a list of course objects
            "created_at": "2024-11-29",  # Add default or current timestamp
        })

        # Return response with the inserted document's ID
        return jsonify({
            "message": "Post created successfully",
            "id": str(result.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@views.route('/ver_institucion/<title>', methods=['GET'])
def update_institucion(title):
    # Recupera la institución desde MongoDB usando el id
    institucion = collection.find_one({"title": title})

    if not institucion:
        return jsonify({"error": "Institución no encontrada"}), 404

    # Recupera los cursos actuales de la institución
    cursos_actuales = institucion.get("courses", [])

    # Renderiza el formulario con los cursos actuales
    return render_template('actualizar.html', institucion=institucion, cursos=cursos_actuales)


@views.route('/actualizar_institucion/<title>', methods=['POST'])
def agregar_cursos(title):
    try:
        # Recupera la institución desde MongoDB
        institucion = collection.find_one({"title": title})

        if not institucion:
            return jsonify({"error": "Institución no encontrada"}), 404

        # Extrae los cursos enviados desde el formulario
        nuevos_cursos = []
        for i in range(10):  # Limitar a 10 cursos como ejemplo
            curso_nombre = request.form.get(f"courses[{i}][name]")
            if not curso_nombre:
                continue  # Si no hay nombre de curso, se salta

            estudiantes = request.form.getlist(f"courses[{i}][students][]")
            nuevos_cursos.append({
                "name": curso_nombre,
                "students": estudiantes
            })

        # Agrega los nuevos cursos a los cursos existentes
        institucion['courses'].extend(nuevos_cursos)

        # Actualiza la institución en la base de datos
        collection.update_one(
            {"title": title},  # Filtro para encontrar la institución
            {"$set": {"courses": institucion['courses']}}  # Actualiza los cursos
        )

        return jsonify({"message": "Cursos agregados exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@views.route('/delete_institucion/<title>', methods=['GET'])
def borrar_institucion(title):
    institucion = collection.find_one({"title": title})

    if not institucion:
        return jsonify({"error": "Institución no encontrada"}), 404

    # Renderiza el formulario con los cursos actuales
    return render_template('eliminar.html', institucion=institucion)



@views.route('/delete_institucion/<title>', methods=['POST'])
def delete_institucion(title):
    try:
        # Buscar la institución por nombre
        institucion = collection.find_one({"title": title})

        if not institucion:
            return jsonify({"error": "Institución no encontrada"}), 404

        # Eliminar la institución de la base de datos
        collection.delete_one({"title": title})  # O usa el ID si es necesario

        return jsonify({"message": "Institución eliminada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@views.route("/info", methods=["GET"])
def get_info():
    # Obtener el documento desde MongoDB
    document = collection.find_one()

    if not document:
        return "Documento no encontrado", 404

    # Convertir el documento a JSON usando bson.json_util.dumps
    document_json = dumps(document)
    document_parsed = json.loads(document_json)

    return render_template("docs.html", document=document_parsed)


@views.route("/documents", methods=["GET"])
def get_documents():
    documents = list(collection.find({}, {"_id": 0}))  # Exclude the _id field
    return jsonify(documents)