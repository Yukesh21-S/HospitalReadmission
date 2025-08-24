from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from model.views import preprocess_patient, cat_model


#
# # Create your views here.
# import joblib
# import pandas as pd
# import numpy as np
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from sklearn.preprocessing import LabelEncoder
#
# # Load pre-trained artifacts
# cat_model = joblib.load("readmission_catboost_model.pkl")
# scaler = joblib.load("scaler.pkl")
# imputer = joblib.load("imputer.pkl")
#
# # Load training columns to align features
# training_columns = joblib.load("training_columns.pkl")  # Save this from your notebook
# label_encoders = joblib.load("label_encoders.pkl")      # Save fitted encoders
#
#
# def preprocess_patient(data: dict):
#     df = pd.DataFrame([data])
#
#     # --- Process blood pressure ---
#     df['systolic'] = df['blood_pressure'].map(lambda x: int(x.split('/')[0]))
#     df['diastolic'] = df['blood_pressure'].map(lambda x: int(x.split('/')[1]))
#     df['pulse_pressure'] = df['systolic'] - df['diastolic']
#     df.drop(columns=["blood_pressure"], inplace=True)
#
#     # --- BMI category ---
#     def bmi_category(bmi):
#         if bmi < 18.5: return 0
#         elif 18.5 <= bmi <= 24.9: return 1
#         elif 25 <= bmi <= 29.9: return 2
#         else: return 3
#     df['bmi_category'] = df['bmi'].map(bmi_category)
#
#     # --- Cholesterol risk ---
#     df['high_cholesterol'] = (df['cholesterol'] > 200).astype(int)
#
#     # --- Encode categorical ---
#     for col, le in label_encoders.items():
#         df[col] = le.transform(df[col].astype(str))
#
#     df = pd.get_dummies(df, columns=['discharge_destination'], drop_first=True)
#
#     # --- Feature engineering ---
#     df['high_risk_age'] = (df['age'] >= 70).astype(int)
#     df['polypharmacy'] = (df['medication_count'] >= 5).astype(int)
#     df['long_stay'] = (df['length_of_stay'] > 14).astype(int)
#     df['multi_comorbidity'] = ((df['diabetes'] == 1) & (df['hypertension'] == 1)).astype(int)
#     df['age_bmi'] = df['age'] * df['bmi']
#     df['stay_meds'] = df['length_of_stay'] * df['medication_count']
#
#     # --- Align with training columns ---
#     df = df.reindex(columns=training_columns, fill_value=0)
#
#     # --- Impute + Scale ---
#     df = pd.DataFrame(imputer.transform(df), columns=training_columns)
#     df = pd.DataFrame(scaler.transform(df), columns=training_columns)
#
#     return df

@api_view(["POST"])
def predict_readmission(request):
    try:
        patient_data = request.data  # JSON from frontend
        processed = preprocess_patient(patient_data)

        proba = cat_model.predict_proba(processed)[:, 1][0]
        pred = int(proba >= 0.5)  # threshold

        return Response({
            "prediction": "Readmit" if pred == 1 else "No Readmission",
            "probability": round(float(proba), 3)
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)
