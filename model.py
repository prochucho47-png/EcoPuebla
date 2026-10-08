import os
import json
from PIL import Image
import google.generativeai as genai

# =================================================================
# La clave se leerá de las variables de entorno (.env o en Render)
# =================================================================
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def predict_image(image_path):
    """
    Función que envía la imagen a la IA de Google Gemini para clasificarla.
    """
    try:
        # Comprobación básica de que se haya puesto la API KEY
        if not api_key:
            return {
                "nombre_comun": "Falta API Key",
                "nombre_cientifico": "Necesitas tu clave de Google AI",
                "tipo": "Desconocido",
                "descripcion": "Verifica que la API Key esté correctamente ingresada.",
                "confianza": 0.0
            }

        # Cargamos el modelo de visión 'Lite' que tiene una cuota diaria mucho mayor
        model = genai.GenerativeModel('gemini-flash-lite-latest')
        
        # Abrimos la imagen guardada con Pillow
        img = Image.open(image_path)
        
        # El "prompt" (instrucción) para la IA
        prompt = """
        Eres un experto biólogo enfocado en la flora y fauna de Puebla, México. 
        Analiza esta imagen y dime qué especie de planta o animal es. 
        Devuelve la respuesta ÚNICAMENTE en formato JSON válido con esta estructura exacta, sin formato markdown extra:
        {
            "nombre_comun": "Ej. Bugambilia",
            "nombre_cientifico": "Ej. Bougainvillea glabra",
            "tipo": "Flora" o "Fauna",
            "descripcion": "Breve descripción de 2 líneas sobre la especie y su presencia en Puebla",
            "confianza": 0.95
        }
        """
        
        # Consultamos a la IA pasándole la instrucción y la imagen
        response = model.generate_content([prompt, img])
        
        # Limpiamos la respuesta por si la IA añade etiquetas markdown (ej. ```json ... ```)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()
            
        # Convertimos el texto a un diccionario de Python
        data = json.loads(raw_text)
        
        # Aseguramos de que el nivel de confianza sea un float numérico (ej. de 0.0 a 1.0)
        data['confianza'] = float(data.get('confianza', 0.9))
        
        return data
        
    except Exception as e:
        error_msg = str(e)
        print("Error al contactar a la IA:", error_msg)
        
        # Detectar si es el error de cuota gratuita por minuto (429)
        if "429" in error_msg or "quota" in error_msg.lower():
            return {
                "nombre_comun": "Servidor Ocupado",
                "nombre_cientifico": "Límite de consultas",
                "tipo": "Pausa requerida",
                "descripcion": "Has superado el límite gratuito de 5 consultas por minuto de la IA. Por favor, espera unos 60 segundos y vuelve a darle al botón de analizar.",
                "confianza": 0.0
            }
            
        return {
            "nombre_comun": "Error de Procesamiento",
            "nombre_cientifico": "-",
            "tipo": "Desconocido",
            "descripcion": f"Hubo un error al procesar la imagen: {error_msg}",
            "confianza": 0.0
        }
