# TYPE-II-DIABETES-MELLITUS-COMPLICATION-RISK-PREDICTOR
Predicting diabetes complications shouldn't be a mystery. I built this to show that high-performance models like XGBoost can be medically transparent. Using SHAP and clinical guidelines, this project bridges the gap between complex AI and the wisdom needed for real-world primary care. Because in healthcare, trust is the best metric.

# 🩺 Interpretable Machine Learning Model for T2DM Complication Risk Prediction

> **An end-to-end clinical data pipeline predicting 3–5 year complication risk for Type 2 Diabetes patients — combining SQL analytics, Power BI dashboards, XGBoost + SHAP explainability, and a live Streamlit clinical decision-support app. Validated against NICE NG28 guidelines.**

<img width="100" height="100" alt="streamlit-logo-png_seeklogo-441815" src="https://github.com/user-attachments/assets/9c7fe8c7-46b5-4b74-8816-6d0dc3e9e125" />
https://type-ii-diabetes-mellitus-complication-risk-predictor-matexjya.streamlit.app/
<img width="112" height="112" alt="python" src="https://github.com/user-attachments/assets/e48653ed-c169-4ebc-a755-512444ee9df8" />
<img width="112" height="112" alt="database" src="https://github.com/user-attachments/assets/ac80778d-ff2f-4016-88a3-5a157a8847ab" />
<img width="115" height="115" alt="download (1)" src="https://github.com/user-attachments/assets/b5410b21-7407-4f4e-85d6-7b95a77918ef" />



---

## 🔍 The Problem

Type 2 Diabetes affects approximately **4.6 million people in the UK**, with nearly 90% of cases carrying risk of serious complications including cardiovascular disease, kidney failure (nephropathy), vision loss (retinopathy), and nerve damage (neuropathy).

While predictive models exist, most function as **"black boxes"** — clinicians are presented with a risk score but given no clinical reasoning behind it. Under NICE NG28 and NHS clinical safety standard DCB0129, a doctor cannot act on a "High Risk" alert without understanding the logic. This project resolves that gap.

---

## 🎯 What This Project Does

This project answers 8 clinical questions using a synthetic cohort of 10,000 UK primary care patients, built across three tools:

| Tool | Purpose |
|---|---|
| **SQL (DBeaver)** | 8 population-level analytical queries answering key clinical questions |
| **Power BI** | 3-page interactive clinical analytics dashboard with risk stratification |
| **Python + Streamlit** | Patient-level ML risk prediction with SHAP explainability, deployed as a live app |

---

## 📊 Key Findings

- **18.6%** of the synthetic cohort experienced a major T2DM complication
- **HbA1c is the dominant risk driver** — moving from target range (<48) to high risk (>64) increases complication probability by **9×** (4.1% → 35.2%)
- **Smoking adds independent risk** at every HbA1c level — a current smoker with above-target HbA1c carries **20.0%** complication rate vs **12.1%** for a non-smoker in the same glycaemic band
- **The Legacy Effect** — a patient under 50 with 20+ years of T2DM carries a **50% complication rate**, nearly identical to an older long-duration patient (51%)
- **Triple Risk Cohort** (HbA1c >64 + Duration >10yrs + Current Smoker) = just **2% of population** but **63.9% complication rate**

---

## 🤖 Model Performance

| Metric | Logistic Regression (Challenger) | XGBoost (Champion) |
|---|---|---|
| AUROC | 0.878 | 0.856 |
| Specificity | 95.88% | 95.15% |
| Sensitivity (Recall) | 44.89% | 43.28% |
| False Negative Rate | 55.11% | 56.72% |
| Clinical Utility (>0.80) | ✅ Pass | ✅ Pass |

**Why XGBoost is the deployed champion despite lower AUROC:** XGBoost integrates natively with SHAP for granular, patient-level explanations — the feature that makes this a clinical decision-support tool rather than just a prediction model.

**On the high false negative rate:** Both models are designed for **targeted high-specificity flagging** — when they flag a patient as high risk, they are right >95% of the time. This aligns with NICE NG28's emphasis on intensive intervention for clearly elevated-risk patients, not blanket screening. The decision threshold can be adjusted for broader screening use cases.

---

## 🔬 SHAP Analysis — Top 5 Risk Drivers

| Rank | Feature | SHAP Importance | Clinical Interpretation |
|---|---|---|---|
| 1 | HbA1c (mmol/mol) | 1.36 | The strongest predictor — glycaemic control dominates |
| 2 | Diabetes Duration (years) | 0.75 | The "legacy effect" — cumulative exposure |
| 3 | Systolic Blood Pressure | 0.43 | Cardiovascular driver |
| 4 | Age | 0.39 | Non-modifiable background risk |
| 5 | BMI | 0.32 | Metabolic driver |

This ranking aligns with UKPDS 35 findings, confirming the model has learned clinically valid biological signals.

---

## 🗂️ Repository Structure

```
t2dm-complication-risk-predictor/
│
├── README.md
├── requirements.txt
├── app.py                                    # Streamlit deployment app
├── champion_xgb.pkl                          # Trained XGBoost pipeline
│
├── notebooks/
│   └── Interpretable_Clinical_ML_Model.ipynb # Full ML pipeline
│
├── sql/
│   └── T2DM_DATA_ANALYSIS_PROJECT_SCRIPTING.sql  # 8 analytical queries
│
├── data/
│   └── t2dm_synthetic_data.csv               # 10,000 patient synthetic cohort
│
├── dashboard/
│   └── T2DM_Risk_Dashboard.pbix              # Power BI 3-page dashboard
│
└── assets/
    ├── dashboard_screenshots/
    │   ├── page1_population_overview.png
    │   ├── page2_clinical_risk_drivers.png
    │   └── page3_ml_risk_intelligence.png
    └── shap_summary.png
```

---

## 🚀 Live Demo

The Streamlit app is deployed at: https://type-ii-diabetes-mellitus-complication-risk-predictor-matexjya.streamlit.app/

Enter a patient's clinical profile (Age, HbA1c, BMI, Blood Pressure, Smoking Status, Ethnicity, Diabetes Duration, LDL Cholesterol) and receive:

- A predicted 3–5 year complication probability with risk tier (Low / Moderate / High)
- A SHAP waterfall chart showing which specific factors are driving the score for that patient
- Plain-English clinical summary with NICE NG28-aligned recommendations

---

## 🛠️ Running Locally

**Prerequisites:** Python 3.9+

```bash
# 1. Clone the repository
git clone https://github.com/your-username/t2dm-complication-risk-predictor.git
cd t2dm-complication-risk-predictor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Streamlit app
streamlit run app.py
```

The app will open at `http://localhost:8501`

**To retrain the model from scratch:**
Open `notebooks/Interpretable_Clinical_ML_Model.ipynb` and run all cells. The notebook generates the synthetic dataset, trains both models, evaluates them, and saves `champion_xgb.pkl`.

> **Note:** `champion_xgb.pkl` was serialized with scikit-learn 1.2.x and xgboost 1.7.x. If you encounter loading errors, retrain using the notebook.

---

## 📋 SQL Analytical Questions

The SQL script answers 8 clinical questions on the full 10,000 patient cohort:

1. **Population complication profile** — overall rate, avg HbA1c, avg years since diagnosis
2. **Complication risk by age group** — which age cohort needs closest monitoring
3. **Is HbA1c the primary driver?** — complication rate across glycaemic control bands
4. **Does smoking compound risk beyond HbA1c?** — interaction analysis
5. **Triple Risk Cohort segmentation** — HbA1c >64 + Duration >10yr + Current Smoker
6. **Ethnic disparities** — complication rates by ethnicity (clinically sensitive, clinically important)
7. **The Legacy Effect** — duration × age interaction on complication risk
8. **ML risk score distribution** — histogram of predicted probabilities across the cohort

---

## 📊 Power BI Dashboard

A 3-page interactive clinical analytics dashboard built from the SQL query outputs:

- **Page 1 — Population Overview:** KPI cards, complication rate by age group, ethnic disparities, risk triage donut
- **Page 2 — Clinical Risk Drivers:** HbA1c band analysis, smoking × HbA1c interaction, triple risk cohort
- **Page 3 — ML Risk Intelligence:** Risk score histogram with threshold lines, legacy effect heatmap, end-to-end pipeline card

The dashboard's 0.3 and 0.7 risk thresholds are identical to those in the Streamlit app — ensuring analytical continuity across tools.

---

## ⚕️ Clinical & Ethical Notes

**This tool is a clinical decision-support aid, not a diagnostic instrument.** All outputs should be interpreted by a qualified clinician in the context of the full patient history.

**Synthetic data:** The dataset was generated using `scipy.stats` and `numpy` with distributions modelled on UK QOF/CPRD profiles. It captures modelled statistical relationships — not novel biological discoveries. A real-world deployment would require HRA-approved NHS data and prospective clinical validation.

**GDPR:** The project uses synthetic data with no identifiable patient information.

**Bias:** SHAP analysis was used to audit model behaviour across demographic subgroups. As with all synthetic data, the model may amplify biases present in the generation parameters.

**False Negative Rate:** Both models have FNR ~55-57%, reflecting a deliberate design choice for high-specificity targeted flagging. Before clinical deployment, threshold calibration and pairing with routine annual HbA1c monitoring would be required.

---

## 🔭 Future Work

- Validate on real NHS Electronic Health Record data (CPRD or THIN)
- Incorporate temporal biomarker trends (HbA1c velocity, BP trajectories) rather than single-point snapshots
- Disaggregate predictions by complication type (retinopathy, nephropathy, neuropathy, cardiovascular)
- Conduct GP-facing usability studies to optimise the Streamlit interface for clinical workflow
- Lower decision threshold for broad screening use cases

---

## 📚 Key References

- Stratton et al. (2000) UKPDS 35 — Association of glycaemia with macrovascular and microvascular complications of T2DM, *BMJ*
- Lundberg & Lee (2017) — A unified approach to interpreting model predictions, *NeurIPS*
- NICE (2022) — Type 2 diabetes in adults: management (NG28)
- Chen & Guestrin (2016) — XGBoost: A scalable tree boosting system, *KDD*
- Rudin (2019) — Stop explaining black box ML models for high-stakes decisions, *Nature Machine Intelligence*

---

## 👤 Author

**Okoh Micheal Oseghale**
MSc Data Science · University of East London · February 2026

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/your-profile)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/your-username)

---

*Built as part of MSc Data Science Dissertation — UEL-DS-7010-91468*
