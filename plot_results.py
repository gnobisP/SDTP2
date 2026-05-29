import pandas as pd
import matplotlib.pyplot as plt


# Carrega os resultados
df = pd.read_csv("results.csv")

# Converte bytes para MB
df["filesize_mb"] = (
    df["filesize"] /
    (1024 * 1024)
)

# Ordena os dados
df = df.sort_values(
    by="filesize_mb"
)

# -------------------------
# Gráfico 1
# Tempo x Tamanho
# -------------------------

plt.figure(figsize=(10, 6))

plt.plot(
    df["filesize_mb"],
    df["download_time"],
    marker="o"
)

plt.title(
    "Tempo de Download x Tamanho do Arquivo"
)

plt.xlabel(
    "Tamanho do Arquivo (MB)"
)

plt.ylabel(
    "Tempo de Download (s)"
)

plt.xticks(
    [0.01, 1, 10]
)

plt.grid(True)

plt.tight_layout()

plt.show()


# -------------------------
# Gráfico 2
# Throughput x Tamanho
# -------------------------

plt.figure(figsize=(10, 6))

plt.plot(
    df["filesize_mb"],
    df["throughput_mb"],
    marker="o"
)

plt.title(
    "Throughput x Tamanho do Arquivo"
)

plt.xlabel(
    "Tamanho do Arquivo (MB)"
)

plt.ylabel(
    "Throughput (MB/s)"
)

plt.xticks(
    [0.01, 1, 10]
)

plt.grid(True)

plt.tight_layout()

plt.show()