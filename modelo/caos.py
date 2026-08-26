import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# MODELO BIOLÓGICO Y CLIMA
# ---------------------------------------------------------------------
TMIN_DESARROLLO = 12.0
TMAX_DESARROLLO = 38.0
A_BRIERE = 0.318905

HR_OPTIMA = 80.0
SIGMA_SECO = 25.0
SIGMA_HUMEDO = 40.0

def R0_laboratorio(T):
    T = np.asarray(T, dtype=float)
    valor = A_BRIERE * T * (T - TMIN_DESARROLLO) * np.sqrt(
        np.maximum(TMAX_DESARROLLO - T, 0)
    )
    return np.where((T > TMIN_DESARROLLO) & (T < TMAX_DESARROLLO), valor, 1e-6)

def factor_humedad(H):
    H = np.asarray(H, dtype=float)
    sigma = np.where(H < HR_OPTIMA, SIGMA_SECO, SIGMA_HUMEDO)
    return np.exp(-((H - HR_OPTIMA) / sigma) ** 2)

def r_por_generacion(T, H):
    R0 = R0_laboratorio(T) * factor_humedad(H)
    return np.log(np.maximum(R0, 1e-6))

def ricker(N, r, K):
    return N * np.exp(r * (1 - N / K))

CICLOS = [
    ("Septiembre", 15,    61),
    ("Octubre",    17.5, 63),
    ("Noviembre",  21,   55),
    ("Diciembre",  23.5, 50),
    ("Enero",      25,   56),
    ("Febrero",    23,   63),
    ("Marzo",      20.5, 64),
    ("Abril",      17,   69),
    ("Mayo",       13.5, 76),
]

# ---------------------------------------------------------------------
# PARÁMETROS REALES DEL LOTE Y PESTICIDAS
# ---------------------------------------------------------------------
HECTAREAS_LOTE = 100.0         # Tamaño del lote

# Precios oficiales por Litro
PRECIO_EXALT_USD_L = 269.50   # Pesticida 1: Spinetoram
PRECIO_TRIVADO_USD_L = 172.00 # Pesticida 2: Spinosad

# Costo directo por mL de producto
COSTO_ML = {
    0: 0.0,
    1: PRECIO_EXALT_USD_L / 1000.0,    # US$ 0.2695 / mL
    2: PRECIO_TRIVADO_USD_L / 1000.0   # US$ 0.1720 / mL
}

# Dosis en mL/ha según marbetes oficiales para cada nivel (1 a 5)
ML_POR_HA = {
    0: {0: 0.0, 1: 0.0,   2: 0.0,   3: 0.0,   4: 0.0,   5: 0.0},
    1: {0: 0.0, 1: 1.04,  2: 2.08,  3: 4.17,  4: 8.33,  5: 16.67}, # Exalt (Base marbete 100 mL/ha = 60 mg/L)
    2: {0: 0.0, 1: 2.81,  2: 5.63,  3: 11.25, 4: 22.50, 5: 45.00}  # TRIVADO (Base marbete 45 mL/ha)
}

# Eficacia (mortalidad)
EFICACIA = {
    0: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
    1: {0: 0.00, 1: 0.21, 2: 0.32, 3: 0.44, 4: 0.56, 5: 0.67}, # Exalt (Spinetoram)
    2: {0: 0.00, 1: 0.11, 2: 0.23, 3: 0.35, 4: 0.49, 5: 0.61}  # TRIVADO (Spinosad)
}

N0_INICIAL = 40.0
K_CAPACIDAD = 1000.0
UMBRAL_DANIO = 500.0

# PENALIZACIONES
PENALIZACION_REPETICION = 1500.0  # Penalización alta para impedir repetición consecutiva de insecticidas
PENALIZACION_UMBRAL = 8.0         # Penalización en USD por cada unidad de N sobre el umbral crítico

# ---------------------------------------------------------------------
# EVALUACIÓN DE ESTRATEGIA (GASTO EN PESTICIDAS + PENALIZACIONES)
# ---------------------------------------------------------------------
def simular_con_estrategia(cromosoma, N0=N0_INICIAL, K=K_CAPACIDAD):
    poblacion = np.zeros(len(CICLOS) + 1)
    poblacion[0] = N0
    N = N0
    
    gasto_producto_total = 0.0
    penalizacion = 0.0
    pest_anterior = 0
    
    for i, (mes, T, H) in enumerate(CICLOS):
        r = r_por_generacion(T, H)
        N = ricker(N, r, K)
        
        pest, dosis = cromosoma[i]
        
        if pest != 0 and dosis != 0:
            mortalidad = EFICACIA[pest][dosis]
            
            # Gasto exclusivo en compra de producto para las hectáreas seleccionadas
            ml_aplicados_ha = ML_POR_HA[pest][dosis]
            gasto_mes = (ml_aplicados_ha * COSTO_ML[pest]) * HECTAREAS_LOTE
            gasto_producto_total += gasto_mes
            
            # Penalización estricta por usar el mismo insecticida en dos meses consecutivos
            if pest == pest_anterior:
                penalizacion += PENALIZACION_REPETICION
                
            pest_anterior = pest
        else:
            mortalidad = 0.0
            
        N = N * (1.0 - mortalidad)
        poblacion[i + 1] = N
        
        if N > UMBRAL_DANIO:
            penalizacion += PENALIZACION_UMBRAL * (N - UMBRAL_DANIO)
            
    # El fitness minimiza el gasto en producto + penalizaciones por repetición/exceso de plaga
    fitness = gasto_producto_total + penalizacion
    
    return poblacion, fitness, gasto_producto_total

# ---------------------------------------------------------------------
# ALGORITMO GENÉTICO
# ---------------------------------------------------------------------
def crear_individuo():
    individuo = []
    for _ in range(len(CICLOS)):
        pest = np.random.choice([0, 1, 2])
        dosis = 0 if pest == 0 else np.random.choice([1, 2, 3, 4, 5])
        individuo.append((pest, dosis))
    return individuo

def cruza(padre1, padre2):
    pt = np.random.randint(1, len(CICLOS))
    return padre1[:pt] + padre2[pt:], padre2[:pt] + padre1[pt:]

def mutar(individuo, prob_mut=0.15):
    individuo_mutado = []
    for pest, dosis in individuo:
        if np.random.rand() < prob_mut:
            pest = np.random.choice([0, 1, 2])
            dosis = 0 if pest == 0 else np.random.choice([1, 2, 3, 4, 5])
        individuo_mutado.append((pest, dosis))
    return individuo_mutado

def optimizar_estrategia(tam_poblacion=80, generaciones=150):
    poblacion = [crear_individuo() for _ in range(tam_poblacion)]
    mejor_individuo = None
    mejor_fitness = float('inf')
    
    for gen in range(generaciones):
        fitnesses = [simular_con_estrategia(ind)[1] for ind in poblacion]
        min_idx = np.argmin(fitnesses)
        
        if fitnesses[min_idx] < mejor_fitness:
            mejor_fitness = fitnesses[min_idx]
            mejor_individuo = poblacion[min_idx]
            
        nueva_poblacion = [mejor_individuo]
        
        while len(nueva_poblacion) < tam_poblacion:
            idx_a = np.random.choice(len(poblacion), 3, replace=False)
            padre1 = min([poblacion[i] for i in idx_a], key=lambda x: simular_con_estrategia(x)[1])
            
            idx_b = np.random.choice(len(poblacion), 3, replace=False)
            padre2 = min([poblacion[i] for i in idx_b], key=lambda x: simular_con_estrategia(x)[1])
            
            hijo1, hijo2 = cruza(padre1, padre2)
            nueva_poblacion.append(mutar(hijo1))
            if len(nueva_poblacion) < tam_poblacion:
                nueva_poblacion.append(mutar(hijo2))
                
        poblacion = nueva_poblacion
        
    return mejor_individuo, mejor_fitness

# ---------------------------------------------------------------------
# EJECUCIÓN
# ---------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    
    mejor_estrategia, fit_opt = optimizar_estrategia()
    
    pob_sin, _, _ = simular_con_estrategia([(0, 0)] * len(CICLOS))
    pob_opt, fit_opt, gasto_prod = simular_con_estrategia(mejor_estrategia)

    dosis_nombres = {0: "Sin Aplicar", 1: "Nivel 1", 2: "Nivel 2", 3: "Nivel 3", 4: "Nivel 4", 5: "Nivel 5"}
    pesticidas_nombres = {0: "Sin Aplicación", 1: "Exalt (Spinetoram)", 2: "TRIVADO (Spinosad)"}
    
    print("=========================================================================================")
    print(f"       ESTRATEGIA OPTIMIZADA CON AG EN BASE A GASTO DE PRODUCTO ({HECTAREAS_LOTE:.0f} HA)")
    print("=========================================================================================")
    for i, (mes, _, _) in enumerate(CICLOS):
        pest, dosis = mejor_estrategia[i]
        mortalidad = EFICACIA[pest][dosis] * 100
        vol_ml = ML_POR_HA[pest][dosis]
        print(f"{mes:<12}: Producto: {pesticidas_nombres[pest]:<21} | Dosis: {dosis_nombres[dosis]:<9} ({vol_ml:5.2f} mL/ha) | Mort: {mortalidad:4.1f}%")

    print("\n-----------------------------------------------------------------------------------------")
    print(f" * GASTO TOTAL EXCLUSIVO EN PRODUCTO ({HECTAREAS_LOTE:.0f} HA):  US$ {gasto_prod:10.2f}")
    print("-----------------------------------------------------------------------------------------")

    etiquetas = ["Inicio"] + [mes for mes, _, _ in CICLOS]
    plt.figure(figsize=(11, 5))
    plt.plot(pob_sin, 'r--o', label="Sin Control (Evolución Natural)", linewidth=2)
    plt.plot(pob_opt, 'g-s', label="Control Optimizado con AG", linewidth=2.5)
    plt.axhline(UMBRAL_DANIO, color='black', linestyle=':', label=f"Umbral de Daño ({UMBRAL_DANIO:.0f})")
    plt.xticks(range(len(etiquetas)), etiquetas, rotation=45, ha="right")
    plt.xlabel("Mes")
    plt.ylabel("Población N")
    plt.title(f"Evolución Poblacional Mantenida con Mínimo Gasto de Producto ({HECTAREAS_LOTE:.0f} ha)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()