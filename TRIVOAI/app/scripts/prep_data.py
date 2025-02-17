import json
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Función para cargar los datos desde los archivos JSON
def cargar_datos():
    with open("/Users/mauriciosobarzo/Desktop/2025/Greensy/Lanzadera/TRIVOAI/TRIVOAI/app/data/off_data.json", "r") as f:
        off_data = json.load(f)

    with open("/Users/mauriciosobarzo/Desktop/2025/Greensy/Lanzadera/TRIVOAI/TRIVOAI/app/data/usda_data.json", "r") as f:
        usda_data = json.load(f)

    return off_data, usda_data

# Función para normalizar los datos
def normalizar_datos():
    # Cargar los datos
    off_data, usda_data = cargar_datos()

    # Extraer las características de los productos
    off_features = [
        [item["calories"], item["fat"], item["carbohydrates"], item["protein"]] for item in off_data
    ]
    usda_features = [
        [item["calories"], item["fat"], item["carbohydrates"], item["protein"]] for item in usda_data
    ]

    # Concatenar los datos
    datos_combinados = np.array(off_features + usda_features)

    # Normalizar los datos usando MinMaxScaler
    scaler = MinMaxScaler()
    datos_normalizados = scaler.fit_transform(datos_combinados)

    return datos_normalizados
