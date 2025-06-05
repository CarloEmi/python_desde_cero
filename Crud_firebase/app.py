import firebase_admin
from flask import Flask, render_template, request, redirect, url_for, flash, session
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import os

load_dotenv()
# Probar conexión

# Inicializar la app de Flask
app = Flask(__name__)
#app.secret_key = 'secret_key'

# Configurar Firebase
app.secret_key = os.getenv('SECRET_KEY')
cred = credentials.Certificate(os.getenv('FIREBASE_KEY'))
firebase_admin.initialize_app(cred)
#cred = credentials.Certificate("config/seapostoles-firebase-adminsdk-tve75-a8232e6679.json")
#initialize_app(cred)
db = firestore.client()
collection_name = 'asistencia'
usuarios_collection = 'usuarios'


# Crear usuario de prueba
prueba_ref = db.collection(usuarios_collection).document("123456789")
prueba_ref.set({
    'dni': '123456789',
    'password': '123456789'
}, merge=True)

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    estudiantes_ref = db.collection(collection_name)
    estudiantes = [doc.to_dict() | {'id': doc.id} for doc in estudiantes_ref.stream()]
    return render_template('index.html', estudiantes=estudiantes)


@app.route('/index_admin')
def index_admin():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Obtener los usuarios administradores desde Firestore
    usuarios_ref = db.collection('usuarios')  # o el nombre de tu colección de usuarios
    usuarios_admin = [doc.to_dict() for doc in usuarios_ref.stream()]
        
    return render_template('index_admin.html', usuarios_admin=usuarios_admin)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        dni = request.form['dni']
        password = request.form['password']
        user_ref = db.collection(usuarios_collection).document(dni)
        user = user_ref.get().to_dict()
        if user and user['password'] == password:
            session['user'] = dni
            return redirect(url_for('index'))
        flash("Credenciales inválidas.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        dni = request.form['dni']
        password = request.form['password']
        db.collection(usuarios_collection).document(dni).set({
            'dni': dni,
            'password': password
        })
        flash("Usuario creado exitosamente.")
        return redirect(url_for('index_admin'))
    return render_template('crear_usuario.html')

@app.route('/editar_usuario/<dni>', methods=['GET', 'POST'])
def editar_usuario(dni):
    if 'user' not in session:
        return redirect(url_for('login'))
    user_ref = db.collection(usuarios_collection).document(dni)
    user = user_ref.get().to_dict()
    if request.method == 'POST':
        password = request.form['password']
        user_ref.update({'password': password})
        flash("Usuario actualizado exitosamente.")
        return redirect(url_for('index'))
    return render_template('editar_usuario.html', user=user)

@app.route('/borrar_usuario/<dni>', methods=['POST'])
def borrar_usuario(dni):
    if 'user' not in session:
        return redirect(url_for('login'))
    db.collection(usuarios_collection).document(dni).delete()
    flash("Usuario eliminado exitosamente.")
    return redirect(url_for('index'))

@app.route('/crear', methods=['GET', 'POST'])
def crear():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$', nombre):
            flash("El nombre solo puede contener letras y espacios.")
            return redirect(url_for('crear'))
        db.collection(collection_name).add({
            'nombre': nombre,
            'asistencias': 0,
            'ausencias': 0,
            'historial': []
        })
        return redirect(url_for('index'))
    return render_template('crear.html')

@app.route('/editar_nombre/<id>', methods=['GET', 'POST'])
def editar_nombre(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    estudiante_ref = db.collection(collection_name).document(id)
    estudiante = estudiante_ref.get().to_dict()

    if not estudiante:
        flash("Estudiante no encontrado.")
        return redirect(url_for('index_admin'))

    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre')
        if nuevo_nombre:
            estudiante_ref.update({'nombre': nuevo_nombre})
            flash("Nombre actualizado correctamente.")
            return redirect(url_for('index'))
        else:
            flash("El nombre no puede estar vacío.")

    return render_template('editar_nombre.html', estudiante=estudiante)


@app.route('/marcar_asistencia/<id>', methods=['GET', 'POST'])
def marcar_asistencia(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    estudiante_ref = db.collection(collection_name).document(id)
    estudiante = estudiante_ref.get().to_dict()
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    # Verificar si ya existe un registro para hoy
    for registro in estudiante['historial']:
        if registro['fecha'] == fecha_hoy:
            flash("Ya se ha registrado asistencia o inasistencia para hoy.")
            return redirect(url_for('index'))

    accion = request.form['accion']
    if accion == 'asistencia':
        estudiante['asistencias'] += 1
        estudiante['historial'].append({
            'fecha': fecha_hoy,
            'estado': 'Presente'
        })
    elif accion == 'ausencia':
        estudiante['ausencias'] += 1
        estudiante['historial'].append({
            'fecha': fecha_hoy,
            'estado': 'Ausente'
        })

    estudiante_ref.update({
        'asistencias': estudiante['asistencias'],
        'ausencias': estudiante['ausencias'],
        'historial': estudiante['historial']
    })
    return redirect(url_for('index'))


@app.route('/historial/<id>')
def historial(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    desde = request.args.get('desde')
    hasta = request.args.get('hasta')

    estudiante_ref = db.collection(collection_name).document(id)
    estudiante = estudiante_ref.get().to_dict()

    if not estudiante:
        flash("Estudiante no encontrado.")
        return redirect(url_for('index_admin'))

    historial_completo = estudiante.get("historial", [])
    historial_filtrado = []
    asistencias_filtradas = 0
    ausencias_filtradas = 0

    for registro in historial_completo:
        fecha = registro['fecha']
        if (not desde or fecha >= desde) and (not hasta or fecha <= hasta):
            historial_filtrado.append(registro)
            if registro['estado'] == 'Presente':
                asistencias_filtradas += 1
            else:
                ausencias_filtradas += 1

    # Ordenar el historial por fecha descendente
    historial_filtrado.sort(key=lambda r: r["fecha"], reverse=True)

    # Actualizar totales en la base de datos
    estudiante_ref.update({
        'asistencias': asistencias_filtradas,
        'ausencias': ausencias_filtradas
    })

    estudiante["historial"] = historial_filtrado
    estudiante["asistencias"] = asistencias_filtradas
    estudiante["ausencias"] = ausencias_filtradas

    return render_template('historial.html', estudiante=estudiante)


@app.route('/editar_historial/<id>/<fecha>', methods=['GET', 'POST'])
def editar_historial(id, fecha):
    if 'user' not in session:
        return redirect(url_for('login'))
    estudiante_ref = db.collection(collection_name).document(id)
    estudiante = estudiante_ref.get().to_dict()
    historial = estudiante.get('historial', [])
    registro = next((r for r in historial if r['fecha'] == fecha), None)

    if not registro:
        flash("Registro no encontrado.")
        return redirect(url_for('historial', id=id))

    if request.method == 'POST':
        nuevo_estado = request.form['estado']
        registro['estado'] = nuevo_estado

        # Recalcular asistencias y ausencias
        asistencias = sum(1 for r in historial if r['estado'] == 'asistencia')
        ausencias = sum(1 for r in historial if r['estado'] == 'ausencia')

        estudiante_ref.update({
            'historial': historial,
            'asistencias': asistencias,
            'ausencias': ausencias
        })

        flash("Historial actualizado exitosamente.")
        return redirect(url_for('historial', id=id))

    return render_template('editar_historial.html', registro=registro, estudiante=estudiante)


@app.route('/borrar/<id>', methods=['POST'])
def borrar(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    db.collection(collection_name).document(id).delete()
    return redirect(url_for('index'))
@app.route('/agregar_asistencia/<id>', methods=['GET', 'POST'])
def agregar_asistencia(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    estudiante_ref = db.collection(collection_name).document(id)
    estudiante = estudiante_ref.get().to_dict()

    if not estudiante:
        flash("Estudiante no encontrado.")
        return redirect(url_for('index_admin'))

    if request.method == 'POST':
        fecha = request.form['fecha']
        estado = request.form['estado']  # Puede ser 'Presente' o 'Ausente'

        # Inicializar historial si no existe
        if 'historial' not in estudiante:
            estudiante['historial'] = []

        # Verificar si ya existe un registro en esa fecha
        existe_registro = any(r['fecha'] == fecha for r in estudiante['historial'])

        if existe_registro:
            flash("Ya existe un registro de asistencia o inasistencia para esa fecha.")
            return redirect(url_for('historial', id=id))

        # Agregar registro al historial
        nuevo_registro = {'fecha': fecha, 'estado': estado}
        estudiante['historial'].append(nuevo_registro)

        # Actualizar contadores
        if estado == 'Presente':
            estudiante['asistencias'] = estudiante.get('asistencias', 0) + 1
        elif estado == 'Ausente':
            estudiante['ausencias'] = estudiante.get('ausencias', 0) + 1

        # Guardar cambios en Firebase
        estudiante_ref.update({
            'historial': estudiante['historial'],
            'asistencias': estudiante['asistencias'],
            'ausencias': estudiante['ausencias']
        })

        flash("Asistencia agregada exitosamente.")
        return redirect(url_for('historial', id=id))

    return render_template('agregar_asistencia.html', estudiante=estudiante)


@app.route('/eliminar_registro/<id>/<fecha>', methods=['POST'])
def eliminar_registro(id, fecha):
    if 'user' not in session:
        return redirect(url_for('login'))

    estudiante_ref = db.collection(collection_name).document(id)
    estudiante = estudiante_ref.get().to_dict()

    if not estudiante or 'historial' not in estudiante:
        flash("Estudiante o historial no encontrado.")
        return redirect(url_for('index_admin'))

    historial = estudiante['historial']
    
    for registro in historial:
        if registro['fecha'] == fecha:
            if registro['estado'].lower() == 'presente':
                estudiante['asistencias'] -= 1
            else:
                estudiante['ausencias'] -= 1
            break

    nuevo_historial = [r for r in historial if r['fecha'] != fecha]

    estudiante_ref.update({
        'historial': nuevo_historial,
        'asistencias': estudiante['asistencias'],
        'ausencias': estudiante['ausencias']
    })

    flash("Registro eliminado correctamente.")
    return redirect(url_for('historial', id=id))


@app.route('/historial_general')
def historial_general():
    if 'user' not in session:
        return redirect(url_for('login'))

    desde = request.args.get('desde')
    hasta = request.args.get('hasta')

    try:
        # Validar y parsear fechas
        if desde:
            datetime.strptime(desde, '%Y-%m-%d')
        if hasta:
            datetime.strptime(hasta, '%Y-%m-%d')
    except ValueError:
        flash("Formato de fecha inválido. Use YYYY-MM-DD.")
        return redirect(url_for('historial_general'))

    historial_filtrado = []
    estudiantes_ref = db.collection(collection_name).stream()

    for est in estudiantes_ref:
        data = est.to_dict()
        historial = data.get('historial', [])
        for registro in historial:
            fecha = registro['fecha']
            if (not desde or fecha >= desde) and (not hasta or fecha <= hasta):
                historial_filtrado.append({
                    'fecha': fecha,  # Formato YYYY-MM-DD para ordenamiento
                    'fecha_display': datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y'),  # Formato para mostrar
                    'nombre': data.get('nombre', 'Sin nombre'),
                    'estado': registro['estado'],
                    'id': est.id
                })

    # Ordenar por fecha descendente
    historial_ordenado = sorted(historial_filtrado, key=lambda x: x['fecha'], reverse=True)
    return render_template('historial_general.html', historial=historial_ordenado)

@app.template_filter('latam_fecha')
def latam_fecha(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        return value


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True) #para FLASK
