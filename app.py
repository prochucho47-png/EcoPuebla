import os
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from model import predict_image

load_dotenv()
app = Flask(__name__)
app.secret_key = "clave_secreta_para_sesiones_seguras" # Clave para cifrar las cookies de sesión

# Las imágenes ahora se guardan en static para poder mostrarlas en el panel de admin
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    """Función auxiliar para conectar a PostgreSQL (local o en Supabase)"""
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        conn = psycopg2.connect(db_url)
    else:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'flora_fauna_puebla'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASS', 'postgres')
        )
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM usuarios WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        # Verificar contraseña encriptada
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['rol'] = user['rol']
            
            if user['rol'] == 'administrador':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos. Intenta de nuevo.')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Destruir la sesión
    return redirect(url_for('login'))

@app.route('/')
def index():
    # Proteger la ruta principal, requiere login
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'], rol=session['rol'])

@app.route('/admin')
def admin_dashboard():
    # Proteger la ruta de administrador
    if 'user_id' not in session or session.get('rol') != 'administrador':
        return redirect(url_for('index'))
        
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Obtener todas las capturas cruzando datos con el nombre del usuario
    cur.execute('''
        SELECT d.*, u.username 
        FROM detecciones d 
        JOIN usuarios u ON d.usuario_id = u.id 
        ORDER BY d.fecha_captura DESC
    ''')
    capturas = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('admin.html', capturas=capturas, username=session['username'])

@app.route('/api/recognize', methods=['POST'])
def recognize_image():
    # Rechazar petición si no hay sesión
    if 'user_id' not in session:
        return jsonify({'error': 'No estás autorizado. Inicia sesión.'}), 401
        
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró archivo'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó archivo'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 1. Analizar imagen con IA
        resultado = predict_image(filepath)
        
        # 2. Guardar registro en Base de Datos
        # Evitamos guardar registros de cuando el sistema da error o se llena la cuota
        if "Error" not in resultado.get("nombre_comun", "") and "Ocupado" not in resultado.get("nombre_comun", ""):
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('''
                    INSERT INTO detecciones (usuario_id, tipo, nombre_comun, nombre_cientifico, imagen_path, nivel_confianza)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (session['user_id'], resultado['tipo'], resultado['nombre_comun'], 
                      resultado['nombre_cientifico'], filepath, resultado['confianza']))
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print("Error al guardar en Base de Datos:", e)
        
        return jsonify({
            'success': True,
            'message': 'Análisis completado',
            'data': resultado
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
