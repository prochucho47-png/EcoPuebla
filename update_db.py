import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def upgrade_database():
    try:
        print("Conectando a la base de datos...")
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        print("Agregando columnas de email y verificación...")
        cur.execute("ALTER TABLE usuarios ADD COLUMN email VARCHAR(255) UNIQUE;")
        cur.execute("ALTER TABLE usuarios ADD COLUMN is_verified BOOLEAN DEFAULT TRUE;") # A los usuarios actuales (admin y juan) los dejamos verificados
        cur.execute("ALTER TABLE usuarios ADD COLUMN verification_token VARCHAR(100);")
        
        conn.commit()
        print("¡Base de datos actualizada con éxito!")
    except psycopg2.errors.DuplicateColumn:
        print("Las columnas ya existían. No se requieren cambios.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    upgrade_database()
