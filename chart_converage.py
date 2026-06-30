import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

data = {
    "Neighborhood": [
        "Cole Valley",
        "Painted Ladies",
        "Lower Haight",
        "W. Addition",
        "Hayes Valley",
        "Pacific Heights",
        "Mission District",
        "Noe Valley",
        "Bernal Heights",
        "Glen Park",
        "Portola",
        "Bayview",
        "Excelsior",
        "Visitacion Valley",
        "Outer Mission",
    ],
    "Coverage (%)": [
        64.2, 58.4, 56.6, 53.7, 45.0,
        30.8, 23.1, 12.0, 7.1,
        2.8, 1.8, 1.4, 0.7, 0.5, 0.1
    ]
}

df = pd.DataFrame(data)

df = df.sort_values("Coverage (%)", ascending=True).reset_index(drop=True)

THRESHOLD = 20.0

colors = ["#2D9E5F" if val >= THRESHOLD else "#B85042"
          for val in df["Coverage (%)"]]

fig, ax = plt.subplots(figsize=(10, 7))


bars = ax.barh(
    df["Neighborhood"],
    df["Coverage (%)"],
    color=colors,
    edgecolor="white",
    linewidth=0.5,
    height=0.65
)

#add the percentage value as a label at the end of each bar
for bar, val in zip(bars, df["Coverage (%)"]):
    ax.text(
        bar.get_width() + 0.5,   # just past the end of the bar
        bar.get_y() + bar.get_height() / 2,  # vertically centered
        f"{val:.1f}%",
        va="center", ha="left",
        fontsize=10, color="#1E293B"
    )

ax.axvline(
    x=THRESHOLD,
    color="#64748B",
    linestyle="--",
    linewidth=1.2,
    alpha=0.7,
    label=f"{THRESHOLD}% threshold"
)

ax.set_xlabel("Known Lighting Data Coverage (%)", fontsize=12, color="#64748B", labelpad=10)
ax.set_title(
    "OSM Lighting Tag Coverage Across 17 San Francisco Neighborhoods",
    fontsize=14, fontweight="bold", color="#1E293B", pad=16
)

fig.text(
    0.13, 0.01,
    "Source: OpenStreetMap via OSMnx  |  Each area scanned within a 1,000m radius  |  "
    "Green = usable coverage (≥20%)  |  Red = too sparse (<20%)",
    fontsize=8.5, color="#94A3B8"
)

ax.set_facecolor("#F8FAFC")
fig.patch.set_facecolor("white")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#E2E8F0")
ax.spines["bottom"].set_color("#E2E8F0")
ax.tick_params(colors="#64748B", labelsize=10)
ax.set_xlim(0, 75)  # leave room for the labels past the bars

green_patch = mpatches.Patch(color="#2D9E5F", label="Usable coverage (≥20%)")
red_patch   = mpatches.Patch(color="#B85042", label="Too sparse for reliable routing (<20%)")
ax.legend(
    handles=[green_patch, red_patch],
    loc="lower right",
    fontsize=10,
    framealpha=0.9,
    edgecolor="#E2E8F0"
)

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("neighborhood_coverage.png", dpi=200, bbox_inches="tight")
print("Saved neighborhood_coverage.png")
plt.show()