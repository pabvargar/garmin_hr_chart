# Garmin Heart Rate Chart (UX-focused redesign)

This project recreates a **Garmin-style heart-rate chart** using raw activity data, with a focus on **improving readability, scaling, and visual clarity** while staying faithful to the original watch UI.

The goal is create a post in LinkedIn to show how **small visualization and UX defaults** (axis scaling, contrast, sizing) can significantly improve how insights are perceived.

---

## What this project does

- Extracts heart-rate data from **Garmin Connect activity exports** (GPX files)
- Rebuilds the heart-rate chart in Python
- Applies UX-driven improvements:
  - Better Y-axis scaling (no unnecessary baseline at 0 bpm)
  - Zone-aware coloring
  - Watch-accurate chart proportions
 
---

## Data source

Garmin activity data downloaded from **Garmin Connect (web version)**  
> Note: exporting GPX files is currently only available on the **web**, not the mobile app.

---

## Tech stack

- Python
- Jupyter Notebooks
- pandas
- matplotlib
- gpxpy
