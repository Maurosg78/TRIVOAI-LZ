from app.modules.recipe_optimization.optimize_recipe import proponer_sustitutos, ajustar_cantidad_ingredientes, ajustar_a_nutriscore
from app.modules.nutrition.nutrition import calcular_nutri_score
receta = {'azúcar': 100, 'harina blanca': 200, 'calorías': 350, 'fibra': 3, 'grasas': 10, 'sal': 1, 'azúcares': 25}

sustitutos_azucar = proponer_sustitutos('azúcar')
print(f'Sustitutos para azúcar: {sustitutos_azucar}')

receta_ajustada = ajustar_cantidad_ingredientes(receta)
print(f'Receta ajustada por cantidad: {receta_ajustada}')

receta_ajustada_nutriscore = ajustar_a_nutriscore(receta)
print(f'Receta ajustada a NutriScore: {receta_ajustada_nutriscore}')

nutri_score = calcular_nutri_score(receta)
print(f'NutriScore: {nutri_score}')
