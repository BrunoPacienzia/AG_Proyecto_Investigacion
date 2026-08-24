import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------
# 1. CALENDARIO REAL DE LA TEMPORADA (5-6 meses ~ 150-180 días)
# ---------------------------------------------------------------------
etapas = ['VE-V2', 'V4-V6', 'V8-V10', 'Floración', 'Llenado grano', 'Madurez']
dias_inicio_etapa = [0, 25, 55, 85, 115, 145]     # día calendario en que arranca cada etapa
dias_fin_etapa    = [25, 55, 85, 115, 145, 175]   # día calendario en que termina
dias_generacion   = [(dias_inicio_etapa[i] + dias_fin_etapa[i]) / 2 for i in range(len(etapas))]
# ^ cada generación de oruga "cierra su ciclo" aprox a mitad de su ventana de etapa

r_por_etapa = [3.9, 3.9, 3.9, 3.9, 3.9, 3.9]   # decrece: menos tejido tierno = menor r
colores_etapa = ['#d4f4dd', '#b8e6c1', '#e8f5a3', '#f5e6a3', '#f5c99b', '#e0e0e0']

n_gen = len(etapas)
N0 = 0.15   # densidad poblacional inicial (normalizada, no depende de control todavía)


# ---------------------------------------------------------------------
# 2. MODELO POBLACIONAL (mapa logístico, r variable por etapa)
# ---------------------------------------------------------------------
# N(t+1) = r_t * N(t) * (1 - N(t))
#
# Es el mismo tipo de mapa caótico que en el modelo base (equivalente en
# comportamiento al de Ricker para estos fines), pero acá 'r' no es
# constante: toma el valor correspondiente a la etapa fenológica que
# atraviesa esa generación. Esto ya alcanza para mostrar caos, sin
# necesidad de meter insecticidas ni optimización.

def simular_poblacion(N0, r_por_etapa):
    """
    Simula la densidad poblacional generación a generación, usando el r
    de la etapa fenológica correspondiente a cada una.

    Retorna
    -------
    list con la densidad poblacional en cada punto (incluye N0 al inicio)
    """
    x = N0
    trayectoria = [x]
    for r_t in r_por_etapa:
        x = r_t * x * (1 - x)
        trayectoria.append(x)
    return trayectoria


trayectoria = simular_poblacion(N0, r_por_etapa)


# ---------------------------------------------------------------------
# 3. GRAFICADO — EJE DE DÍAS REALES CON ETAPAS FENOLÓGICAS
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 6.5))

# Franjas de fondo por etapa fenológica
for i, etapa in enumerate(etapas):
    ax.axvspan(dias_inicio_etapa[i], dias_fin_etapa[i], color=colores_etapa[i], alpha=0.5, zorder=0)
    ax.text((dias_inicio_etapa[i] + dias_fin_etapa[i]) / 2, 1.05, etapa,
            transform=ax.get_xaxis_transform(), ha='center', fontsize=9, rotation=0)

dias_x = [0] + dias_generacion  # día 0 = inicio, luego un punto por generación

ax.plot(dias_x, trayectoria, 'o-', color='firebrick', linewidth=2.5, markersize=7,
         label='Dinámica poblacional (sin control)')

ax.set_xlabel('Día calendario de la temporada')
ax.set_ylabel('Densidad poblacional N (normalizada)')
ax.set_title('Dinámica caótica de la oruga cogollera — temporada completa de maíz (~175 días)\n'
             'Mapa logístico con r variable por etapa fenológica', pad=35)
ax.legend(loc='upper left', fontsize=9)
ax.set_xlim(0, 178)
ax.grid(alpha=0.2)

fig.subplots_adjust(top=0.85)
plt.savefig('./temporada_dinamica_caotica.png', dpi=150)
print("Gráfico guardado.")


# ---------------------------------------------------------------------
# 4. TABLA RESUMEN
# ---------------------------------------------------------------------
print("\n" + "=" * 55)
print(f"{'Etapa':<15}{'Día':<10}{'r':<6}{'N (densidad)'}")
print("=" * 55)
for i, etapa in enumerate(etapas):
    print(f"{etapa:<15}{dias_generacion[i]:<10.0f}{r_por_etapa[i]:<6}{trayectoria[i+1]:.3f}")

print(f"\nPoblación final: {trayectoria[-1]:.3f}")