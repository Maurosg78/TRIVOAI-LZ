import numpy as np
import requests
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import json

# Constantes
AZUCAR = 'azúcar'
UMBRAL_SIMILARIDAD = 5  # Umbral para comparar nutrientes

# 1. Obtener datos de un producto desde Open Food Facts por código de barras
def obtener_producto(barcode):
    """Obtiene los datos de un producto desde Open Food Facts usando su código de barras."""
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    return response.json()

def procesar_datos(producto):
    """Procesa los datos de un producto para extraer ingredientes y nutrientes."""
    ingredientes = producto.get("product", {}).get("ingredients_text", "")
    nutrientes = producto.get("product", {}).get("nutriments", {})
    
    # Normalizar los nutrientes
    nutrientes_normalizados = {
        'energia': nutrientes.get('energy-kcal', 0),
        'proteinas': nutrientes.get('proteins', 0),
        'grasas': nutrientes.get('fat', 0),
        'carbohidratos': nutrientes.get('carbohydrates', 0),
        'fibra': nutrientes.get('fiber', 0)
    }
    return ingredientes, nutrientes_normalizados

# 2. Entrenamiento de la red neuronal
def entrenar_modelo(datos_entrada, etiquetas_salida):
    """Entrena un modelo de red neuronal para predecir un valor basado en los nutrientes."""
    modelo = Sequential([
        Dense(64, input_dim=5, activation='relu'),  # 5 nutrientes como entrada
        Dense(32, activation='relu'),
        Dense(1, activation='linear')  # Salida de una sola variable continua
    ])
    modelo.compile(optimizer=Adam(), loss='mse')
    modelo.fit(datos_entrada, etiquetas_salida, epochs=100, batch_size=5, verbose=1)
    return modelo

# 3. Funciones de comparación de ingredientes y sustitutos
def son_similares(ingrediente1, ingrediente2):
    """Compara dos ingredientes para determinar si son similares en base a sus nutrientes."""
    return all(
        abs(ingrediente1.get(key, 0) - ingrediente2.get(key, 0)) <= UMBRAL_SIMILARIDAD
        for key in ingrediente1 if isinstance(ingrediente1[key], (int, float))
    )

def generar_reemplazo(ingrediente_original, base_datos_ingredientes):
    """Genera reemplazos para un ingrediente basado en una base de datos de ingredientes."""
    return [ingrediente for ingrediente in base_datos_ingredientes if son_similares(ingrediente_original, ingrediente)]

# 4. Ajuste de receta según dureza del agua
def obtener_contenido_calcio(agua_tipo):
    """Obtiene el contenido de calcio en el agua (simulado)."""
    return 80 if agua_tipo == "Valencia" else 50  # mg/L de calcio

def ajustar_textura_con_agua(agua_tipo, contenido_calcio, receta):
    """Ajusta la receta según el tipo de agua y su contenido de calcio/magnesio."""
    if agua_tipo == "Valencia" and contenido_calcio > 50:  # Agua dura
        receta["agua"] *= 0.9  # Reducir agua en un 10%
        receta["sal"] *= 0.9  # Reducir sal en un 10%
    else:
        receta["agua"] *= 1.05  # Aumentar agua en un 5%
    return receta

# 5. Evaluar el impacto nutricional local
def evaluar_impacto_nutrientes_locales(ingrediente, perfil_local):
    """Evalúa el impacto nutricional de un ingrediente en comparación con un perfil local."""
    return {nutriente: ingrediente[nutriente] - perfil_local[nutriente] for nutriente in perfil_local}

# 6. Ajustes para NutriScore
def ajustar_a_nutriscore(receta):
    """Ajusta los ingredientes para mejorar el NutriScore de la receta."""
    if receta.get(AZUCAR, 0) > 50:
        receta[AZUCAR] *= 0.8  # Reducir azúcar en un 20%
    if receta.get('fibra', 0) < 5:
        receta['fibra'] += 2  # Aumentar fibra
    return receta

def ajustar_a_nutriscore_aplus(receta):
    """Ajusta la receta para acercarse al NutriScore A+."""
    if receta.get('azúcar', 0) > 30:
        receta['azúcar'] *= 0.7  # Reducir azúcar en un 30% más
    if receta.get('fibra', 0) < 8:
        receta['fibra'] += 3  # Aumentar fibra para mejorar el NutriScore
    if receta.get('calorías', 0) > 300:
        receta['calorías'] *= 0.9  # Reducir calorías para mejorar la calificación
    return receta

# 7. Cargar datos de USDA
def cargar_datos_usda():
    """Carga los datos de nutrientes desde el archivo 'ingredientes_usda.json'."""
    with open('app/scripts/ingredientes_usda.json', 'r') as f:
        return json.load(f)

def obtener_reemplazos(ingrediente_buscar, data):
    """Consulta los datos de USDA para obtener nutrientes y encontrar ingredientes similares."""
    return [
        ingrediente for ingrediente, nutrientes in data.items()
        if all(abs(nutrientes.get(key, 0) - ingrediente_buscar.get(key, 0)) <= UMBRAL_SIMILARIDAD
            for key in ingrediente_buscar if isinstance(ingrediente_buscar[key], (int, float)))
    ]

# 8. Ajustar receta para NutriScore A+
def ajustar_receta_a_nutriscore(receta, reemplazos, meta_nutrientes):
    """Ajusta la receta para que se aproxime a los valores de NutriScore A+."""
    for ingrediente, cantidad in receta.items():
        if ingrediente in reemplazos:
            receta[ingrediente] = reemplazos[ingrediente]['cantidad']
        if ingrediente in meta_nutrientes:
            diferencia = meta_nutrientes[ingrediente] - receta.get(ingrediente, 0)
            if diferencia > 0:
                receta[ingrediente] += diferencia  # Aumentar la cantidad
            else:
                receta[ingrediente] = max(receta[ingrediente] + diferencia, 0)  # Reducir la cantidad, pero no por debajo de 0
    return receta

# Ejemplo de uso
def main():
    # Paso 1: Obtener datos de un producto
    barcode = "1234567890123"  # Código de barras de ejemplo
    producto = obtener_producto(barcode)
    ingredientes, nutrientes_normalizados = procesar_datos(producto)
    print(f"Ingredientes: {ingredientes}")
    print(f"Nutrientes: {nutrientes_normalizados}")

    # Paso 2: Entrenar el modelo
    X = np.array([[200, 5, 10, 50, 3], [250, 7, 12, 55, 4], [180, 4, 8, 45, 2], [220, 6, 11, 52, 3]])
    y = np.array([250, 300, 230, 270])  # Salida (etiquetas)
    modelo = entrenar_modelo(X, y)

    # Paso 3: Generar reemplazos para una receta basada en nutrientes
    base_datos_ingredientes = [
        {'ingrediente': 'aceite de oliva', 'energia': 884, 'proteinas': 0, 'grasas': 100, 'carbohidratos': 0, 'fibra': 0},
        {'ingrediente': 'aceite de girasol', 'energia': 884, 'proteinas': 0, 'grasas': 100, 'carbohidratos': 0, 'fibra': 0}
    ]
    ingrediente_original = {'ingrediente': 'aceite de oliva', 'energia': 884, 'proteinas': 0, 'grasas': 100, 'carbohidratos': 0, 'fibra': 0}
    reemplazos = generar_reemplazo(ingrediente_original, base_datos_ingredientes)
    print("Mejores reemplazos encontrados:", reemplazos)

    # Paso 4: Ajustar receta según dureza del agua
    agua_valencia = "Valencia"  # Agua dura de Valencia
    contenido_calcio = obtener_contenido_calcio(agua_valencia)
    receta = {'agua': 200, 'harina': 500, 'sal': 10, 'azúcar': 40, 'fibra': 4, 'calorías': 350}
    receta_ajustada = ajustar_textura_con_agua(agua_valencia, contenido_calcio, receta)
    print("Receta ajustada según dureza del agua:", receta_ajustada)

    # Paso 5: Evaluar el impacto nutricional local
    perfil_local_arroz = {"fibra": 1.8, "proteinas": 7.0, "carbohidratos": 78.0, "calorias": 365}
    ingrediente_arroz = {"fibra": 2.0, "proteinas": 6.5, "carbohidratos": 80.0, "calorias": 370.0}
    impacto = evaluar_impacto_nutrientes_locales(ingrediente_arroz, perfil_local_arroz)
    print("Impacto nutricional local:", impacto)

    # Paso 6: Ajustar receta para NutriScore A+
    receta_ajustada_nutriscore = ajustar_a_nutriscore_aplus(receta)
    print("Receta ajustada a NutriScore A+: ", receta_ajustada_nutriscore)

    # Paso 7: Prueba de reemplazos
    data = cargar_datos_usda()
    ingrediente_buscar = {'energia': 642, 'proteinas': 33.5, 'grasas': 10.6, 'carbohidratos': 108, 'fibra': 30.0}
    reemplazos = obtener_reemplazos(ingrediente_buscar, data)
    print(f"Reemplazos encontrados: {reemplazos}")

if __name__ == "__main__":
    main()