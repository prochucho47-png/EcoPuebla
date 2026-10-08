import os
import psycopg2
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

def init_db():
    try:
        print("Conectando a PostgreSQL...")
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            conn = psycopg2.connect(db_url)
        else:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "flora_fauna_puebla"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASS", "postgres")
            )
        cur = conn.cursor()
        
        print("Creando tablas...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(20) DEFAULT 'usuario'
            );
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS detecciones (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER REFERENCES usuarios(id),
                tipo VARCHAR(50),
                nombre_comun VARCHAR(100),
                nombre_cientifico VARCHAR(150),
                imagen_path VARCHAR(255) NOT NULL,
                nivel_confianza NUMERIC(5, 2),
                fecha_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        print("Insertando usuarios de prueba...")
        admin_hash = generate_password_hash('admin123')
        user_hash = generate_password_hash('usuario123')
        
        cur.execute("INSERT INTO usuarios (username, password_hash, rol) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", 
                    ('admin', admin_hash, 'administrador'))
        cur.execute("INSERT INTO usuarios (username, password_hash, rol) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", 
                    ('juan', user_hash, 'usuario'))
        
        conn.commit()
        cur.close()
        conn.close()
        print("¡Base de datos inicializada con éxito! Usuarios: 'admin' y 'juan' creados.")
    except Exception as e:
        print("Error al inicializar la base de datos. Verifica que PostgreSQL esté corriendo y las credenciales en el archivo .env sean correctas.")
        print("Detalle del error:", e)

if __name__ == '__main__':
    init_db()
