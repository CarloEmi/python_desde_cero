from flask import Flask, render_template, request, redirect, url_for, flash, session
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime, timedelta
import re
'''
try:
    db.collection('test').add({'message': 'Conexión exitosa'})
    print("Conectado exitosamente a Firebase")
except Exception as e:
    print("Error conectando a Firebase:", e)
'''
# Probar conexión

# Inicializar la app de Flask
app = Flask(__name__)
app.secret_key = 'secret_key'

# Configurar Firebase
cred = credentials.Certificate("config/seapostoles-firebase-adminsdk-tve75-5335e1f419.json")
initialize_app(cred)
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
    estudiante_ref = db.collection(collection_name).document(id)
    estudiante = estudiante_ref.get().to_dict()
    return render_template('historial.html', estudiante=estudiante)

@app.route('/editar_historial/<id>/<fecha>', methods=['GET', 'POST'])
def editar_historial(id, fecha):
    if 'user' not in session:
        return redirect(url_for('login'))
    estudiante_ref = db.collection(collection_name).document(id)
    estudiante = estudiante_ref.get().to_dict()
    registro = next((r for r in estudiante['historial'] if r['fecha'] == fecha), None)
    if not registro:
        flash("Registro no encontrado.")
        return redirect(url_for('historial', id=id))
    if request.method == 'POST':
        estado = request.form['estado']
        registro['estado'] = estado
        estudiante_ref.update({'historial': estudiante['historial']})
        flash("Historial actualizado exitosamente.")
        return redirect(url_for('historial', id=id))
    return render_template('editar_historial.html', registro=registro, estudiante=estudiante)

@app.route('/borrar/<id>', methods=['POST'])
def borrar(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    db.collection(collection_name).document(id).delete()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
