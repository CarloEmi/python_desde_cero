
# Materia: Paradigmas y lenguajes de programación
## CRUD con Firebase
### Estudiante: Pereyra Carlos Emiliano
### Docente: Pautsch Germán
### UNaM - FCEQyN

## Descripción del Programa
Este programa permite gestionar la asistencia de estudiantes de una materia utilizando un CRUD (Crear, Leer, Actualizar, Eliminar) conectado a Firebase como base de datos. El sistema incluye funcionalidades de autenticación mediante DNI y contraseña, lo que asegura que solo usuarios autorizados puedan realizar modificaciones. A su vez permite un CRUD de usuarios administradores.

El sistema permite:
1. Registrar estudiantes y administradores
2. Registrar asistencias o inasistencias con una fecha específica (dentro del último mes).
3. Visualizar el historial de asistencias e inasistencias por estudiante.
4. Modificar registros erróneos en el historial.
5. Gestionar usuarios administradores para el sistema (crear, editar y eliminar).

## Funcionalidades del Programa
### 1. Autenticación de Usuarios
- **Inicio de sesión:** Los usuarios deben ingresar su DNI y contraseña para acceder al sistema.
- **Usuario de prueba:**
  - **DNI:** 123456789
  - **Contraseña:** 123456789
- **Gestión de usuarios:**
  - Crear nuevos usuarios.
  - Editar la contraseña de usuarios existentes.
  - Eliminar usuarios.

### 2. Gestión de Estudiantes
- **Registrar estudiantes:** Se permite agregar nuevos estudiantes, ingresando un nombre válido (solo letras y espacios).
- **Validaciones:**
  - El nombre no puede contener números ni caracteres especiales.

### 3. Registro de Asistencias e Inasistencias
- **Selección de fecha:**
  - El usuario puede registrar asistencias o inasistencias seleccionando una fecha específica dentro del último mes.
  - No se permite registrar para fechas futuras ni fuera del rango permitido.
- **Evitar duplicados:**
  - No se permite registrar más de un estado (asistencia o inasistencia) para una misma fecha.

### 4. Historial de Asistencias
- **Visualización:**
  - Muestra el historial completo de asistencias e inasistencias por estudiante.
  - Indica la fecha y el estado correspondiente (Presente o Ausente).
- **Edición:**
  - Permite corregir registros erróneos en el historial.

### 5. Eliminación
- **Estudiantes:** Los estudiantes pueden ser eliminados del sistema.
- **Registros:** Los usuarios pueden editar los registros del historial, pero no eliminarlos por completo.
- **Usuarios:** Se pueden eliminar usuarios administradores.

## Controles Implementados
1. **Validación de entrada:**
   - Los campos de texto validan caracteres para evitar errores del usuario.
   - Las fechas están restringidas al último mes.
2. **Autenticación:**
   - Solo usuarios autenticados pueden acceder al sistema.
3. **Mensajes de retroalimentación:**
   - El sistema muestra mensajes al usuario cuando ocurre un error (por ejemplo, registro duplicado o datos inválidos).
4. **Flash messages:**
   - Notificaciones breves para informar acciones exitosas o errores.

## Requisitos para Ejecutar el Programa
### Herramientas Necesarias
1. **Python 3.10+**
2. **Paquetes necesarios:**
   - Flask
   - Firebase Admin SDK
   - Bootstrap para las plantillas HTML

### Configuración Previa
1. Crear un proyecto en [Firebase Console](https://console.firebase.google.com/).
2. Descargar el archivo `firebase-config.json` desde Firebase y colocarlo en la carpeta `config` del proyecto.
3. Instalar las dependencias con:
   ```bash
   pip install flask firebase-admin
   ```

### Ejecución
1. Clona o descarga el proyecto.
2. Navega al directorio del proyecto en la terminal.
3. Ejecuta el programa con:
   ```bash
   python app.py
   ```
4. Accede al sistema desde el navegador en `http://127.0.0.1:5000`.

## Uso del Programa
### Flujo Principal
1. **Iniciar sesión:** Ingresa con el usuario de prueba o uno creado previamente.
2. **Gestionar estudiantes:** Agrega, visualiza o elimina estudiantes desde la interfaz.
3. **Registrar asistencias:** Selecciona un estudiante y registra su estado (Presente o Ausente) para una fecha válida.
4. **Historial:** Consulta o edita los registros existentes en el historial de un estudiante.
5. **Gestión de usuarios:** Crea o modifica usuarios administradores según sea necesario.

### Ejemplo de Uso
1. Inicia sesión con el usuario:
   - DNI: `123456789`
   - Contraseña: `123456789`
2. Registra un nuevo estudiante con nombre "Juan Pérez".
3. Marca la asistencia para "Juan Pérez" en la fecha `2024-12-01`.
4. Consulta el historial de "Juan Pérez" y verifica el registro.
5. Si te equivocas, corrige el estado desde el historial.

