import requests
import json

# Tu API Key de USDA
USDA_API_KEY = "VoUZcYnQ04PKmQU6x34ZlvJaMmgb4ad7dQCwMK38"
URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

def procesar_datos_usda(data):
    """Procesa los datos obtenidos de la API de USDA para extraer nutrientes y almacenarlos en un formato adecuado."""
    # Aquí procesamos los datos que nos devuelve la API de USDA. Asegúrate de ajustar según la estructura del JSON de la API.
    if 'foods' in data and len(data['foods']) > 0:
        food_data = data['foods'][0]  # Suponiendo que solo tomamos el primer alimento de la lista
        nutrientes = food_data.get('foodNutrients', [])

        ingredientes = {nutriente['nutrientName']: nutriente['value'] for nutriente in nutrientes}

        # Aquí puedes filtrar o modificar los datos según sea necesario
        return ingredientes
    else:
        return {}

def obtener_ingredientes_de_usda(ingrediente, max_results=10):
    params = {
        "query": ingrediente,
        "api_key": USDA_API_KEY,
        "pageSize": max_results
    }
    response = requests.get(URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def almacenar_datos(ingredientes, archivo="ingredientes_usda.json"):
    """Almacena los datos obtenidos de USDA en un archivo JSON."""
    with open(archivo, 'w') as f:
        json.dump(ingredientes, f, indent=4)

# Ejemplo de consulta y almacenamiento de datos
ingrediente = "garbanzo"
data = obtener_ingredientes_de_usda(ingrediente)
if data:
    ingredientes = procesar_datos_usda(data)
    almacenar_datos(ingredientes)
print("Datos almacenados en 'ingredientes_usda.json'")
