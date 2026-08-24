import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# CURVAS DE TEMPERATURA Y HUMEDAD
# ---------------------------------------------------------------------
TMIN_DESARROLLO = 12.0
TMAX_DESARROLLO = 38.0
A_BRIERE = 0.318905  # estimar/calibrar

HR_OPTIMA = 80.0
SIGMA_SECO = 25.0
SIGMA_HUMEDO = 40.0


def R0_laboratorio(T):
    T = np.asarray(T, dtype=float)

    valor = A_BRIERE * T * (T - TMIN_DESARROLLO) * np.sqrt(
        np.maximum(TMAX_DESARROLLO - T, 0)
    )

    return np.where(
        (T > TMIN_DESARROLLO) & (T < TMAX_DESARROLLO),
        valor,
        1e-6
    )


def factor_humedad(H):
    H = np.asarray(H, dtype=float)

    sigma = np.where(
        H < HR_OPTIMA,
        SIGMA_SECO,
        SIGMA_HUMEDO
    )

    return np.exp(-((H - HR_OPTIMA) / sigma) ** 2)


def r_por_generacion(T, H):
    R0 = R0_laboratorio(T) * factor_humedad(H)

    return np.log(np.maximum(R0, 1e-6))


def ricker(N, r, K):
    return N * np.exp(r * (1 - N / K))


# ---------------------------------------------------------------------
# CLIMA POR GENERACIÓN
# Septiembre a mayo
# Cada generación utiliza directamente el T y HR correspondientes
# al mes.
# ---------------------------------------------------------------------
CICLOS = [
    # (mes, T media °C, HR media %)
    ("Septiembre", 15,   61),
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
# INCERTIDUMBRE PARA EL MONTE CARLO
# ---------------------------------------------------------------------
N0_MIN, N0_MAX = 5, 15
K_MIN, K_MAX = 900, 1100

SIMULACIONES = 100


def simular_una_trayectoria(ciclos, N0_min, N0_max, K_min, K_max):
    """
    Corre una trayectoria del Monte Carlo.

    La temperatura y la humedad NO son aleatorias:
    se utilizan directamente los valores correspondientes
    a cada mes definidos en CICLOS.

    La incertidumbre está únicamente en:
        - población inicial N0
        - capacidad de carga K
    """

    # Población inicial aleatoria
    N0 = np.random.uniform(N0_min, N0_max)

    # Capacidad de carga aleatoria
    K = np.random.uniform(K_min, K_max)

    poblacion = np.zeros(len(ciclos) + 1)
    poblacion[0] = N0

    N = N0

    for i, (mes, T, H) in enumerate(ciclos):

        # T y H son los valores fijos del mes
        r = r_por_generacion(T, H)

        # Evolución mediante Ricker
        N = ricker(N, r, K)

        poblacion[i + 1] = N

    return poblacion


# ---------------------------------------------------------------------
# SIMULACIÓN MONTE CARLO
# ---------------------------------------------------------------------
if __name__ == "__main__":

    trayectorias = np.zeros(
        (SIMULACIONES, len(CICLOS) + 1)
    )

    for s in range(SIMULACIONES):

        trayectorias[s] = simular_una_trayectoria(
            CICLOS,
            N0_MIN,
            N0_MAX,
            K_MIN,
            K_MAX
        )

    # -----------------------------------------------------------------
    # ESTADÍSTICOS
    # -----------------------------------------------------------------
    promedio = trayectorias.mean(axis=0)

    p10 = np.percentile(
        trayectorias,
        10,
        axis=0
    )

    p90 = np.percentile(
        trayectorias,
        90,
        axis=0
    )

    etiquetas = ["Inicio"] + [
        mes for mes, _, _ in CICLOS
    ]

    # -----------------------------------------------------------------
    # GRÁFICO
    # -----------------------------------------------------------------
    plt.figure(figsize=(11, 6))

    for s in range(SIMULACIONES):
        plt.plot(
            trayectorias[s],
            alpha=0.15
        )

    plt.plot(
        promedio,
        linewidth=2.5,
        label="Promedio"
    )

    plt.fill_between(
        range(len(promedio)),
        p10,
        p90,
        alpha=0.15,
        label="Percentil 10-90"
    )

    plt.xticks(
        range(len(etiquetas)),
        etiquetas,
        rotation=45,
        ha="right"
    )

    plt.xlabel("Generación")
    plt.ylabel("Población (u. relativas)")

    plt.title(
        f"Monte Carlo - {SIMULACIONES} simulaciones\n"
        "Incertidumbre en N0 y K"
    )

    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        "./salidas/montecarlo_plaga.png",
        dpi=150
    )

    # -----------------------------------------------------------------
    # RESULTADO FINAL
    # -----------------------------------------------------------------
    print(
        f"Población final -> promedio: {promedio[-1]:.1f}, "
        f"P10: {p10[-1]:.1f}, "
        f"P90: {p90[-1]:.1f}"
    )