import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import warnings
import json
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="T2DM Complication Risk Predictor",
    page_icon="🩺",
    layout="centered"
)

# ── Load model ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    pipeline = joblib.load("champion_xgb.pkl")
    
    # ── DIRECT BASE_SCORE FIX FOR XGBOOST 3.1+ / SHAP COMPATIBILITY ──────────
    # XGBoost 3.1+ stores base_score as '[value]' (with brackets).
    # SHAP's TreeExplainer calls float() on this string and crashes.
    # Fix: extract the booster, strip the brackets from the config, reload it.
    classifier = pipeline.named_steps['classifier']
    booster = classifier.get_booster()
    
    try:
        cfg = json.loads(booster.save_config())
        param = cfg['learner']['learner_model_param']
        if 'base_score' in param:
            bs = param['base_score']
            if isinstance(bs, str):
                param['base_score'] = bs.strip('[]')
            elif isinstance(bs, list):
                param['base_score'] = str(bs[0]).strip('[]')
        booster.load_config(json.dumps(cfg))
    except Exception:
        pass
    # ── END FIX ───────────────────────────────────────────────────────────────
    
    return pipeline

model_pipeline = load_model()

# ── Feature name setup ────────────────────────────────────────────────────────
num_cols = ['Age', 'BMI', 'HbA1c_mmol', 'Systolic_BP', 'LDL_Cholesterol', 'Diabetes_Duration_Years']
cat_cols = ['Sex', 'Ethnicity', 'Smoking_Status']

preprocessor   = model_pipeline.named_steps['preprocessor']
model_internal = model_pipeline.named_steps['classifier']

cat_feature_names = preprocessor.named_transformers_['cat'].get_feature_names_out(cat_cols).tolist()
all_feature_names = num_cols + cat_feature_names

clean_labels = {
    'HbA1c_mmol':              'HbA1c (Blood Sugar)',
    'Diabetes_Duration_Years': 'Years with Diabetes',
    'Systolic_BP':             'Systolic Blood Pressure',
    'BMI':                     'Body Mass Index',
    'Age':                     'Patient Age',
    'LDL_Cholesterol':         'LDL Cholesterol',
}

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🩺 T2DM Complication Risk Predictor")
st.markdown(
    "**Interpretable ML for UK Primary Care** · XGBoost + SHAP · Validated against NICE NG28"
)
st.markdown("---")
st.markdown(
    "Enter patient clinical values below. The model will predict the 3–5 year risk of a major "
    "diabetes complication and explain exactly which factors are driving that score."
)

# ── Input form ────────────────────────────────────────────────────────────────
st.subheader("Patient Clinical Profile")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age (years)", min_value=30, max_value=95, value=60, step=1)
    bmi = st.number_input("BMI (kg/m²)", min_value=18.5, max_value=55.0, value=31.0, step=0.1)
    hba1c = st.number_input(
        "HbA1c (mmol/mol)",
        min_value=35.0, max_value=110.0, value=58.0, step=0.5,
        help="Normal <48 · Target <53 · High risk >64"
    )
    systolic_bp = st.number_input(
        "Systolic Blood Pressure (mmHg)",
        min_value=90, max_value=200, value=135, step=1
    )

with col2:
    ldl = st.number_input(
        "LDL Cholesterol (mmol/L)",
        min_value=0.5, max_value=6.0, value=3.0, step=0.1
    )
    duration = st.number_input(
        "Diabetes Duration (years)",
        min_value=0.0, max_value=40.0, value=7.0, step=0.5
    )
    sex      = st.selectbox("Sex", ["Male", "Female"])
    ethnicity = st.selectbox("Ethnicity", ["White", "Asian", "Black", "Other"])

smoking = st.selectbox("Smoking Status", ["Non-Smoker", "Ex-Smoker", "Current Smoker"])

st.markdown("---")

# ── Prediction ────────────────────────────────────────────────────────────────
if st.button("🔍 Generate Risk Prediction", use_container_width=True):

    patient_data = pd.DataFrame([{
        'Age':                     age,
        'BMI':                     bmi,
        'HbA1c_mmol':              hba1c,
        'Systolic_BP':             systolic_bp,
        'LDL_Cholesterol':         ldl,
        'Diabetes_Duration_Years': duration,
        'Sex':                     sex,
        'Ethnicity':               ethnicity,
        'Smoking_Status':          smoking
    }])

    risk_prob = model_pipeline.predict_proba(patient_data)[0][1]
    risk_pct  = round(float(risk_prob) * 100, 1)

    # ── Risk tier display ─────────────────────────────────────────────────────
    st.subheader("Predicted Complication Risk")

    if risk_prob < 0.30:
        tier, colour, emoji = "LOW RISK", "green", "🟢"
        message = (
            "This patient's current profile suggests a low likelihood of a major complication "
            "in the next 3–5 years. Routine monitoring and standard care apply."
        )
    elif risk_prob < 0.70:
        tier, colour, emoji = "MODERATE RISK", "orange", "🟡"
        message = (
            "This patient shows several risk markers that warrant closer monitoring. "
            "Consider intensifying HbA1c control and reviewing cardiovascular risk factors. "
            "NICE NG28 recommends increased follow-up frequency."
        )
    else:
        tier, colour, emoji = "HIGH RISK", "red", "🔴"
        message = (
            "This patient is at high risk of a major complication. "
            "Urgent clinical review is indicated. Priority actions: optimise glycaemic control, "
            "address blood pressure, and assess for early signs of nephropathy or retinopathy."
        )

    st.markdown(
        f"""
        <div style='background-color: rgba(0,0,0,0.04); padding: 24px;
                    border-radius: 12px; text-align: center; margin-bottom: 16px;'>
            <div style='font-size: 48px;'>{emoji}</div>
            <div style='font-size: 36px; font-weight: 700; color: {colour};'>{risk_pct}%</div>
            <div style='font-size: 20px; font-weight: 600; color: {colour};
                        margin-bottom: 12px;'>{tier}</div>
            <div style='font-size: 14px; color: #555; max-width: 500px; margin: 0 auto;'>
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── SHAP explanation ──────────────────────────────────────────────────────
    import shap

    st.subheader("Why did the model give this score?")
    st.markdown(
        "The chart below shows a **tug-of-war** for this specific patient. "
        "🔴 Red bars push the risk **higher**. 🔵 Blue bars pull the risk **lower**. "
        "The longer the bar, the stronger the influence."
    )

    transformed_patient = preprocessor.transform(patient_data)

    # Use the booster directly — the base_score fix was already applied at load time
    explainer   = shap.TreeExplainer(model_internal.get_booster())
    shap_values = explainer.shap_values(transformed_patient)

    if isinstance(shap_values, list):
        sv = shap_values[1][0]
    else:
        sv = shap_values[0]

    shap_df = pd.DataFrame({'feature': all_feature_names, 'shap_value': sv})
    shap_df['label'] = shap_df['feature'].map(lambda x: clean_labels.get(x, x))
    shap_df['abs']   = shap_df['shap_value'].abs()
    shap_df = shap_df.sort_values('abs', ascending=True).tail(8)

    fig, ax = plt.subplots(figsize=(8, 4))
    colours = ['#e74c3c' if v > 0 else '#3498db' for v in shap_df['shap_value']]
    ax.barh(shap_df['label'], shap_df['shap_value'], color=colours)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlabel("Impact on Risk Score  (positive = increases risk)", fontsize=11)
    ax.set_title("Patient-Level Risk Drivers (SHAP)", fontsize=13, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # ── Clinical summary ──────────────────────────────────────────────────────
    st.subheader("Clinical Summary")

    top_risk_factors    = shap_df[shap_df['shap_value'] > 0].sort_values('abs', ascending=False)
    top_protect_factors = shap_df[shap_df['shap_value'] < 0].sort_values('abs', ascending=False)

    summary_lines = []

    if not top_risk_factors.empty:
        top_names = top_risk_factors['label'].head(3).tolist()
        summary_lines.append(
            f"**Primary risk drivers:** {', '.join(top_names)}. "
            "These are the factors most actively pushing this patient's risk score upward."
        )

    if not top_protect_factors.empty:
        prot_names = top_protect_factors['label'].head(2).tolist()
        summary_lines.append(
            f"**Protective factors:** {', '.join(prot_names)}. "
            "These are currently helping to offset some of the risk."
        )

    if hba1c > 64:
        summary_lines.append(
            "⚠️ **HbA1c is above 64 mmol/mol.** Per NICE NG28, this level is associated with "
            "significantly accelerated risk of microvascular complications. Glycaemic optimisation "
            "should be the primary clinical priority."
        )
    elif hba1c > 53:
        summary_lines.append(
            "📋 **HbA1c is above the 53 mmol/mol target.** Consider reviewing medication adherence "
            "and lifestyle factors to bring this within the recommended range."
        )

    if systolic_bp > 140:
        summary_lines.append(
            "⚠️ **Systolic BP exceeds 140 mmHg.** NICE NG28 recommends a target below 140/90 for "
            "most T2DM patients, and below 130/80 in those with kidney or cardiovascular involvement."
        )

    if smoking == "Current Smoker":
        summary_lines.append(
            "🚬 **Current smoker status** is a significant independent risk multiplier. "
            "Smoking cessation support should be offered and documented."
        )

    for line in summary_lines:
        st.markdown(f"- {line}")

    st.markdown("---")
    st.caption(
        "⚕️ This tool is a clinical decision-support aid, not a diagnostic instrument. "
        "All outputs should be interpreted in the context of the full patient history by a qualified clinician. "
        "Model validated against NICE NG28 guidelines · XGBoost AUROC 0.856 · LR AUROC 0.878"
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Built as part of MSc Data Science Dissertation · University of East London · "
    "Okoh Micheal Oseghale · February 2026"
)
