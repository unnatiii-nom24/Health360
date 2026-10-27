# Health360: Healthcare Risk & Disease Analysis

Health360 is a student project that explores patient health indicators and chronic-disease patterns through an interactive web dashboard. It uses Python, Flask, Pandas, HTML/CSS and Plotly charts.

## Project structure

```text
Health360_GitHub_Project/
├── backend/
│   └── app.py                  # Flask routes, data preparation and chart summaries
├── data/
│   └── smart_healthcare_dataset.csv
├── frontend/
│   ├── templates/              # Dashboard, Story and About pages
│   └── static/
│       └── style.css
├── notebooks/                  # Space for optional analysis notebooks
├── src/                        # Space for reusable analysis modules
├── requirements.txt
├── .gitignore
└── README.md
```

## Features

- Dashboard with patient summary metrics and interactive visualizations.
- Filters for age group, gender, BMI category and exercise level.
- Charts for age distribution, exercise, blood pressure, disease flags, lifestyle indicators and BMI-related patterns.
- Guided Story page and a project About page.
- JSON summary endpoint at `/api/summary`.
- Responsive layout for desktop and smaller screens.

## Run locally on Windows

Install Python 3.10 or newer, then open a terminal in the project folder and run:

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python backend/app.py
```

Open <http://127.0.0.1:5000> in your browser. Keep the terminal running while you use the site; press `Ctrl+C` to stop it.

If the `py` command is unavailable, use `python` instead.

## Upload to GitHub

1. Download and extract the project ZIP.
2. Open your GitHub repository.
3. Choose **Add file → Upload files**.
4. Open the extracted `Health360_GitHub_Project` folder and drag its *contents* into the GitHub upload area (including folders, `README.md`, `requirements.txt`, and `.gitignore`).
5. Add a commit message such as `Add Health360 healthcare analytics project`, then click **Commit changes**.

GitHub's browser uploader uploads the files inside the folder; uploading the ZIP itself will only store the archive, not show the project files individually.

## Dataset and interpretation notes

The included CSV contains 5,000 records and 16 columns. The app creates age and BMI groups for visualization. Exercise values are displayed as Low, Moderate and High using the mapping in the code; confirm those numeric codes against the dataset documentation if available.

In the supplied data, `health_risk_score` has only one unique value (100), so it should not be interpreted as a useful ranking measure. The charts describe patterns in this dataset and are not medical advice or a clinical diagnosis. Plotly is loaded from a CDN, so an internet connection is needed for charts to render.

## Tools used

- Python
- Flask
- Pandas
- Plotly.js
- HTML and CSS
