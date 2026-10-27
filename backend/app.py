from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__, template_folder=str(PROJECT_ROOT / "frontend" / "templates"), static_folder=str(PROJECT_ROOT / "frontend" / "static"), static_url_path="/static")
DATA_PATH = PROJECT_ROOT / "data" / "smart_healthcare_dataset.csv"

def load_data():
    df = pd.read_csv(DATA_PATH)
    # Human-readable labels for the binary fields in this dataset.
    df["age_group"] = pd.cut(
        df["age"], bins=[17, 30, 40, 50, 60, 70, float("inf")],
        labels=["18–30", "31–40", "41–50", "51–60", "61–70", "Over 70"]
    ).astype(str)
    df["bmi_category"] = pd.cut(
        df["bmi"], bins=[-float("inf"), 18.5, 25, 30, float("inf")],
        labels=["Underweight", "Normal", "Overweight", "Obese"]
    ).astype(str)
    # Convert numeric codes to strings for consistent filters.
    df["exercise_label"] = df["exercise_level"].map({0: "Low", 1: "Moderate", 2: "High"}).fillna(df["exercise_level"].astype(str))
    return df

DATA = load_data()

def clean_records(filters):
    d = DATA.copy()
    for key, col in [("age_group", "age_group"), ("gender", "gender"), ("bmi_category", "bmi_category"), ("exercise", "exercise_label")]:
        val = filters.get(key, "All")
        if val and val != "All":
            d = d[d[col].astype(str) == val]
    return d

def chart_payload(d):
    # Plotly is loaded in the browser from CDN; all chart data comes from this app.
    def group_counts(col, label=None):
        s = d.groupby(col, dropna=False).size().reset_index(name="count")
        s[col] = s[col].astype(str)
        return {"x": s[col].tolist(), "y": s["count"].tolist(), "name": label or col}
    age_counts = group_counts("age_group", "Patients")
    exercise_counts = group_counts("exercise_label", "Patients")
    bmi_counts = group_counts("bmi_category", "Patients")
    bp = d.groupby("age_group", observed=False)["blood_pressure"].mean().reset_index()
    bp["age_group"] = bp["age_group"].astype(str)
    disease = []
    for col, label in [("heart_disease","Heart disease"),("diabetes","Diabetes"),("stroke","Stroke")]:
        disease.append({"name": label, "value": int(d[col].sum())})
    lifestyle = []
    for col, label in [("smoking","Smoking flag"),("alcohol","Alcohol flag"),("fatigue","Fatigue flag"),("chest_pain","Chest pain flag")]:
        lifestyle.append({"name": label, "value": round(float(d[col].mean()*100), 1)})
    bmi_disease = []
    for cat, sub in d.groupby("bmi_category", observed=False):
        if len(sub):
            bmi_disease.append({"category": str(cat), "heart_rate": round(float(sub["heart_disease"].mean()*100),1),
                                "diabetes_rate": round(float(sub["diabetes"].mean()*100),1)})
    heat = d.groupby(["bmi_category","exercise_label"], observed=False)["heart_disease"].mean().reset_index()
    heat = heat.dropna()
    return {
        "age": age_counts,
        "exercise": exercise_counts,
        "bmi": bmi_counts,
        "bp": {"x":bp["age_group"].tolist(),"y":bp["blood_pressure"].round(2).tolist()},
        "disease": disease,
        "lifestyle": lifestyle,
        "bmi_disease": bmi_disease,
        "heat": {"x":heat["exercise_label"].astype(str).tolist(),"y":heat["bmi_category"].astype(str).tolist(),
                 "z":(heat["heart_disease"]*100).round(1).tolist()},
    }

@app.route("/")
def home():
    filters = {
        "age_group": request.args.get("age_group", "All"),
        "gender": request.args.get("gender", "All"),
        "bmi_category": request.args.get("bmi_category", "All"),
        "exercise": request.args.get("exercise", "All"),
    }
    d = clean_records(filters)
    if len(d) == 0:
        d = DATA.iloc[0:0].copy()
    total = len(d)
    stats = {
        "patients": total,
        "heart": round(float(d["heart_disease"].mean()*100),1) if total else 0,
        "diabetes": round(float(d["diabetes"].mean()*100),1) if total else 0,
        "stroke": round(float(d["stroke"].mean()*100),1) if total else 0,
        "avg_bp": round(float(d["blood_pressure"].mean()),1) if total else 0,
        "avg_bmi": round(float(d["bmi"].mean()),1) if total else 0,
    }
    return render_template(
        "index.html", filters=filters, stats=stats, charts=chart_payload(d),
        options={
            "age_group": ["All"] + sorted(DATA["age_group"].dropna().unique().tolist()),
            "gender": ["All"] + sorted(DATA["gender"].dropna().unique().tolist()),
            "bmi_category": ["All"] + ["Underweight","Normal","Overweight","Obese"],
            "exercise": ["All","Low","Moderate","High"],
        },
        data_quality={
            "rows": len(DATA), "columns": len(pd.read_csv(DATA_PATH, nrows=0).columns),
            "missing": int(DATA.isna().sum().sum()), "duplicates": int(DATA.duplicated().sum()),
            "risk_unique": int(DATA["health_risk_score"].nunique()),
        }
    )

@app.route("/story")
def story():
    # Story scenes are calculated from the full dataset to give a guided narrative.
    return render_template("story.html", charts=chart_payload(DATA),
        patient_count=len(DATA),
        heart_pct=round(float(DATA["heart_disease"].mean()*100),1),
        diabetes_pct=round(float(DATA["diabetes"].mean()*100),1),
        stroke_pct=round(float(DATA["stroke"].mean()*100),1),
        avg_bp=round(float(DATA["blood_pressure"].mean()),1),
        avg_bmi=round(float(DATA["bmi"].mean()),1),
        risk_unique=int(DATA["health_risk_score"].nunique()))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/api/summary")
def api_summary():
    d = clean_records({
        "age_group": request.args.get("age_group","All"),
        "gender": request.args.get("gender","All"),
        "bmi_category": request.args.get("bmi_category","All"),
        "exercise": request.args.get("exercise","All")
    })
    return jsonify({"records": len(d), "charts": chart_payload(d)})

if __name__ == "__main__":
    app.run(debug=True)
