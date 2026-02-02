# ----------------------------
# 1) Initial Jupyter workbook set up and include garmin running data
# ----------------------------

import os, sys
os.getcwd(), sys.executable

pip install gpxpy pandas matplotlib

gpx_path = "morning_run.gpx"


# ----------------------------
# 2) Build dataframe (Heart rate + km + zone)
# ----------------------------

import pandas as pd
from math import radians, sin, cos, asin, sqrt

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

rows = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            hr = None
            for ext in point.extensions:
                for child in ext:
                    if child.tag.endswith("hr"):
                        hr = int(child.text)

            if point.time and hr is not None:
                rows.append({
                    "time": point.time,
                    "bpm": hr,
                    "lat": point.latitude,
                    "lon": point.longitude,
                })

df = pd.DataFrame(rows)
df["time"] = pd.to_datetime(df["time"]).dt.tz_localize(None)

# cumulative distance in km
dist_km = [0.0]
for i in range(1, len(df)):
    dist_km.append(
        dist_km[-1] + haversine_km(
            df.loc[i-1, "lat"], df.loc[i-1, "lon"],
            df.loc[i, "lat"],   df.loc[i, "lon"]
        )
    )

df["km"] = dist_km

# HR zones
def hr_zone(bpm):
    if bpm > 172: return "Z5"
    if bpm >= 155: return "Z4"
    if bpm >= 135: return "Z3"
    if bpm >= 119: return "Z2"
    return "Z1"

df["zone"] = df["bpm"].apply(hr_zone)
avg_hr = df["bpm"].mean()

df.head()


# ----------------------------
# 3) Plot a Garmin-like heart-rate chart with improved UI, sized to match the original watch display
# ----------------------------

import matplotlib.pyplot as plt

# Light smoothing to mimic Garmin UI rendering (keeps trend, reduces jaggedness)
df["bpm_smooth"] = df["bpm"].rolling(window=5, center=True, min_periods=1).mean()

# The graph has the exact size of the chart of my picture of the garmin watch
fig, ax = plt.subplots(figsize=(4.2, 2.5), dpi=100)

# Black background
fig.patch.set_facecolor("black")
ax.set_facecolor("black")

zone_colors = {
    "Z1": "#A9A9A9",  # grey
    "Z2": "#01E6E9",  # blue
    "Z3": "#0AD25B",  # green
    "Z4": "#FF8C00",  # orange
    "Z5": "#FF0000",  # red
}

LINE_WIDTH = 2.8

# Zone-colored HR line
start = 0
for i in range(1, len(df)):
    if df["zone"].iloc[i] != df["zone"].iloc[i - 1]:
        seg = df.iloc[start:i]
        ax.plot(
            seg["km"], seg["bpm_smooth"],
            color=zone_colors[seg["zone"].iloc[0]],
            linewidth=LINE_WIDTH,
            solid_capstyle="round",
            solid_joinstyle="round",
            antialiased=True,
        )
        start = i

seg = df.iloc[start:]
ax.plot(
    seg["km"], seg["bpm_smooth"],
    color=zone_colors[seg["zone"].iloc[0]],
    linewidth=LINE_WIDTH,
    solid_capstyle="round",
    solid_joinstyle="round",
    antialiased=True,
)

# Average HR line
ax.axhline(
    avg_hr,
    color="white",
    linewidth=1.2,
    linestyle=(0, (4, 4)),
    alpha=0.9,
)

# Axis limits
ax.set_xlim(0, 16)
ax.set_ylim(110, 210)

# Configuring axis similar to Garmin (FIXED kwargs)
AXIS_FONT = {
    "fontfamily": "DejaVu Sans",
    "fontsize": 18,
    "fontweight": "medium",
    "color": "#CFCFCF",
}

# X axis shown
ax.set_xticks([6.9, 13.82])
ax.set_xticklabels(["6.9 km", "13.8 km"], **AXIS_FONT)

# Y axis ticks on the RIGHT, with labels
ax.set_yticks([130, 200])
ax.set_yticklabels(["130", "200"], **AXIS_FONT)
ax.yaxis.set_ticks_position("right")
ax.yaxis.set_label_position("right")

# Hide Y-axis spines (no vertical line), keep labels
ax.spines["left"].set_visible(False)
ax.spines["right"].set_visible(False)

# No tick marks; keep label color consistent
ax.tick_params(axis="y", length=0, colors="#CFCFCF")
ax.tick_params(axis="x", length=0, colors="#CFCFCF")

# Keep X axis subtle
ax.spines["bottom"].set_color("white")
ax.spines["bottom"].set_alpha(0.3)

# Hide unused spines
ax.spines["top"].set_visible(False)

# Clean look
ax.set_xlabel("")
ax.set_ylabel("")
ax.grid(False)

# Tight margins for screenshot
plt.subplots_adjust(left=0.05, right=0.99, top=0.95, bottom=0.18)

GUIDE_LINES = [130, avg_hr, 200]

for y in GUIDE_LINES:
    ax.axhline(
        y=y,
        color="white",
        linewidth=1,
        alpha=0.35,
        linestyle="-" if y != avg_hr else (0, (4, 4)),
        zorder=0
    )

ax.axhline(130, color="white", linewidth=1, alpha=0.25, zorder=0)
ax.axhline(200, color="white", linewidth=1, alpha=0.25, zorder=0)

plt.savefig(
    "garmin_hr_chart_2.png",
    dpi=100,
    facecolor="black",
    bbox_inches="tight",
    pad_inches=0
)

plt.show()
