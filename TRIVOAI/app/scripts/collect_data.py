import requests
import json

# Función para consultar datos de Open Food Facts (OFF)
def obtener_datos_off():
    url = "https://world.openfoodfacts.org/data/product"
    params = {
        "fields": "product_name,calories,fat,carbohydrates,proteins",
        "page_size": 10,  # Limitar la cantidad de datos por consulta para pruebas
    }
    response = requests.get(url, params=params)
    data = response.json()
    productos = data.get("products", [])

    return [
        {
            "product_name": producto.get("product_name"),
            "calories": producto.get("calories_100g"),
            "fat": producto.get("fat_100g"),
            "carbohydrates": producto.get("carbohydrates_100g"),
            "protein": producto.get("proteins_100g"),
        }
        for producto in productos
    ]

# Función para consultar datos de USDA
def obtener_datos_usda():
    url = "https://api.nal.usda.gov/fdc/v1/foods/list"
    params = {
        "api_key": "YOUR_API_KEY",  # Reemplazar con tu propia API key de USDA
        "fields": "description,foodNutrients",
        "limit": 10,  # Limitar la cantidad de datos por consulta para pruebas
    }
    response = requests.get(url, params=params)
    data = response.json()

    return [
        {
            "product_name": item["description"],
            "calories": item["foodNutrients"][0]["value"],  # Asegúrate de mapear correctamente los nutrientes
            "fat": item["foodNutrients"][1]["value"],
            "carbohydrates": item["foodNutrients"][2]["value"],
            "protein": item["foodNutrients"][3]["value"],
        }
        for item in data
    ]

# Función para guardar los datos en los archivos JSON
def guardar_datos():
    off_data = obtener_datos_off()
    usda_data = obtener_datos_usda()

    with open("/Users/mauriciosobarzo/Desktop/2025/Greensy/Lanzadera/TRIVOAI/TRIVOAI/app/data/off_data.json", "w") as f:
        json.dump(off_data, f, indent=4)

    with open("/Users/mauriciosobarzo/Desktop/2025/Greensy/Lanzadera/TRIVOAI/TRIVOAI/app/data/usda_data.json", "w") as f:
        json.dump(usda_data, f, indent=4)

# Llamar la función para guardar los datos
if __name__ == "__main__":
    guardar_datos()
