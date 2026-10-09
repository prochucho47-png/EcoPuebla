import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def upgrade_database():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        print("Agregando columnas de geolocalización...")
        cur.execute("ALTER TABLE detecciones ADD COLUMN latitud FLOAT;")
        cur.execute("ALTER TABLE detecciones ADD COLUMN longitud FLOAT;")
        
        conn.commit()
        print("¡Base de datos actualizada con éxito!")
    except psycopg2.errors.DuplicateColumn:
        print("Las columnas latitud/longitud ya existían.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    upgrade_database()
