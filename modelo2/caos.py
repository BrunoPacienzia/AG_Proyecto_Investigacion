import numpy as np
import matplotlib.pyplot as plt


def ricker(N, r, K):
    return N * np.exp(r * (1 - N / K))


def simular(N0, r, K, generaciones):
    N = np.zeros(generaciones + 1)
    N[0] = N0
    for i in range(generaciones):
        N[i + 1] = ricker(N[i], r, K)
    return N


K = 1000
GENERACIONES = 40
N0_A = 50.0
N0_B = 50.1 
N0_C = 50.2

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=False)

for ax, r, titulo in zip(axes, [1.0, 4.5], ["r=1.0 (no caótico)", "r=3.5 (caótico)"]):
    traj_A = simular(N0_A, r, K, GENERACIONES)
    traj_B = simular(N0_B, r, K, GENERACIONES)
    traj_C = simular(N0_C, r, K, GENERACIONES)

    ax.plot(traj_A, label=f"N0={N0_A}", marker='o', markersize=3)
    ax.plot(traj_B, label=f"N0={N0_B}", marker='o', markersize=3, linestyle='--')
    ax.plot(traj_C, label=f"N0={N0_C}", marker='o', markersize=3, linestyle=':')
    ax.set_xlabel("Generación")
    ax.set_ylabel("Población")
    ax.set_title(titulo)
    ax.legend()
    ax.grid(alpha=0.3)

    diferencia_final = abs(traj_A[-1] - traj_B[-1])
    print(f"{titulo}: diferencia final entre trayectorias = {diferencia_final:.4f}")

fig.tight_layout()
fig.savefig("./salidas/sensibilidad_inicial.png", dpi=150)