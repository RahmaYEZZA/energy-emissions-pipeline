"""Example of using the warehouse: a chart built from mart_change_since_1990."""
import duckdb
import matplotlib.pyplot as plt

from pipeline.config import WAREHOUSE

COUNTRIES = ["United Kingdom", "Germany", "France", "Italy", "Spain", "United States", "Poland"]

con = duckdb.connect(str(WAREHOUSE), read_only=True)
df = con.execute("""
    SELECT country, co2_change_pct
    FROM mart_change_since_1990
    WHERE country IN (SELECT UNNEST(?))
    ORDER BY co2_change_pct DESC
""", [COUNTRIES]).df()

GRID, MUTED = "#e6e5e0", "#898781"
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": GRID,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "axes.axisbelow": True, "font.size": 11})
fig, ax = plt.subplots(figsize=(8, 3.8))
bars = ax.barh(df["country"], df["co2_change_pct"], color="#2a78d6", height=0.6)
ax.bar_label(bars, labels=[f"{v:+.0f}%" for v in df["co2_change_pct"]], padding=4, color="#52514e")
ax.axvline(0, color="#52514e", linewidth=1)
ax.set_title("Change in CO₂ emissions since 1990 (from mart_change_since_1990)",
             loc="left", fontweight="bold")
ax.grid(axis="y", visible=False); ax.margins(x=0.15)
fig.tight_layout(); fig.savefig("images/co2_change_since_1990.png", dpi=150)
print(df.to_string(index=False))
