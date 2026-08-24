import numpy as np
import matplotlib.pyplot as plt

# VARIABLES

TEMPERATURA = 23
HUMEDAD = 0.2
# PRECIPITACIONES = ""
# VIENTO = ""

# PARÁMETROS

# % de plantas infestadas al inicio (0-100)
N0 = 1
# capacidad de carga en %
K = 100
# cantidad de días a simular
dias = 10
# temperatura óptima para el crecimiento de la población
Topt = 23.5
# desviación estándar de la temperatura
sigma_T = 5
# constante de decaimiento de la humedad
b = 0.1
# tasa de crecimiento máxima
rmax = 1.0


def tasa_crecimiento(T, H):
    ft = np.exp(-(T - Topt)**2 / (2 * sigma_T**2))
    fh = np.exp(-(b * H))
    r = rmax * ft * fh
    return r


def logistico(N, r, K):
    """
    Calcula el % de plantas infestadas del día siguiente (modelo SI discreto).

    N/K es la fracción de plantas infestadas y (1 - N/K) la fracción de
    plantas sanas disponibles para contagiarse. Se clipea a [0, K] porque
    con r alto (zona caótica) el mapa puede overshootear por encima de K
    o incluso dar valores negativos, que no tienen sentido como % de
    plantas.
    """
    N_siguiente = N + r * N * (1 - N / K)
    return np.clip(N_siguiente, 0, K)


def simular_poblacion(N0, r, K, dias):
    """
    Simula la evolución del % de plantas infestadas durante 'dias' pasos.

    Parámetros
    ----------
    N0 : float -> % de plantas infestadas inicial (0-100)
    r  : float -> tasa de contagio
    K  : float -> capacidad de carga (100 = todo el lote infestado)
    dias : int -> cantidad de días a simular

    Retorna
    -------
    np.array con el % de plantas infestadas día a día (incluye el día 0)
    """
    poblacion = np.zeros(dias + 1)
    poblacion[0] = N0
    for t in range(dias):
        poblacion[t + 1] = logistico(poblacion[t], r, K)
    return poblacion


def diagrama_bifurcacion(K=100, r_min=0.5, r_max=111111.0, n_r=800,
                          transitorio=200, iteraciones=100):
    """
    Genera los datos del diagrama de bifurcación variando r.

    Para cada valor de r se simula el sistema, se descartan los
    primeros pasos ("transitorio", para eliminar el efecto de la
    condición inicial) y se grafican los valores restantes.
    """
    valores_r = np.linspace(r_min, r_max, n_r)
    fig, ax = plt.subplots(figsize=(10, 6))

    for r in valores_r:
        N = K / 2  # condición inicial arbitraria (50% de plantas infestadas)
        for _ in range(transitorio):
            N = logistico(N, r, K)
        valores_N = []
        for _ in range(iteraciones):
            N = logistico(N, r, K)
            valores_N.append(N)
        ax.plot([r] * len(valores_N), valores_N, ',k', alpha=0.6)

    ax.set_xlabel("Tasa de crecimiento (r)")
    ax.set_ylabel("Plantas infestadas de equilibrio (%)")
    ax.set_title("Diagrama de bifurcación - Modelo logístico (SI vegetal)")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------
# 4. EJECUCIÓN DE PRUEBA
# ---------------------------------------------------------------------
if __name__ == "__main__":

    r = tasa_crecimiento(TEMPERATURA, HUMEDAD)
    print(f"r calculado a partir del clima: {r:.3f}")

    poblacion = simular_poblacion(N0, r, K, dias)
    print("=== Evolución del % de plantas infestadas (prueba) ===")
    for dia, N in enumerate(poblacion):
        print(f"Día {dia} -> {N:.1f}% de plantas infestadas")

    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(poblacion, marker="o")
    ax1.set_xlabel("Día")
    ax1.set_ylabel("Plantas infestadas (%)")
    ax1.set_title(f"Evolución de la infestación (r={r:.2f}, K={K})")
    fig1.tight_layout()
    fig1.savefig("evolucion_poblacion.png", dpi=150)

    # --- Diagrama de bifurcación ---
    fig2 = diagrama_bifurcacion(K=K)
    fig2.savefig("bifurcacion.png", dpi=150)