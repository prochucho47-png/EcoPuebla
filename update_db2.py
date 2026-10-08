import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def upgrade_database():
    try:
        print("Conectando a la base de datos...")
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        print("Agregando columna reset_token...")
        cur.execute("ALTER TABLE usuarios ADD COLUMN reset_token VARCHAR(100);")
        
        conn.commit()
        print("¡Base de datos actualizada con éxito!")
    except psycopg2.errors.DuplicateColumn:
        print("La columna reset_token ya existía.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    upgrade_database()
