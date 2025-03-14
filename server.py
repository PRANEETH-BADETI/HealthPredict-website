from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import xgboost as xgb  
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load the heart disease model
with open('models/heart_model.pkl', 'rb') as f:
    heart_model = pickle.load(f)

# Load the stroke model (XGBoost)
with open('models/stroke_model_xgb.pkl', 'rb') as f:
    stroke_model = pickle.load(f)

# Load the diabetes model (XGBoost)
with open('models/diabetes_xgb_model.pkl', 'rb') as f:
    diabetes_model = pickle.load(f)

# Scaler for heart disease features
heart_scaler = MinMaxScaler()
heart_numerical_cols = ['age', 'resting bp s', 'cholesterol', 'max heart rate', 'oldpeak']
heart_min_values = [28, 0, 0, 60, -2.6]
heart_max_values = [77, 200, 603, 202, 6.2]
heart_scaler.fit(np.array([heart_min_values, heart_max_values]))

# Scaler for stroke features
stroke_scaler = MinMaxScaler()
stroke_numerical_cols = ['age', 'avg_glucose_level', 'bmi']
stroke_min_values = [0.08, 55.12, 10.3]
stroke_max_values = [82.0, 271.74, 97.6]
stroke_scaler.fit(np.array([stroke_min_values, stroke_max_values]))

# Scaler for diabetes features
diabetes_scaler = MinMaxScaler()
diabetes_numerical_cols = ['age', 'bmi', 'HbA1c_level', 'blood_glucose_level']
diabetes_min_values = [0.08, 10.01, 3.5, 80]
diabetes_max_values = [80.0, 95.69, 9.0, 300]
diabetes_scaler.fit(np.array([diabetes_min_values, diabetes_max_values]))

# Feature order for heart model
heart_feature_order = [
    'age', 'sex', 'chest pain type', 'resting bp s', 'cholesterol',
    'fasting blood sugar', 'resting ecg', 'max heart rate', 'exercise angina',
    'oldpeak', 'ST slope'
]

# Feature order for stroke model
stroke_feature_order = [
    'age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi',
    'gender_Male', 'gender_Other', 'ever_married_Yes',
    'work_type_Never_worked', 'work_type_Private', 'work_type_Self-employed', 'work_type_children',
    'Residence_type_Urban', 'smoking_history_formerly smoked', 'smoking_history_never smoked', 'smoking_history_smokes'
]

# Feature order for diabetes model
diabetes_feature_order = [
    'age', 'hypertension', 'heart_disease', 'bmi', 'HbA1c_level', 'blood_glucose_level',
    'gender_Male', 'gender_Other',
    'smoking_history_current', 'smoking_history_ever', 'smoking_history_former',
    'smoking_history_never', 'smoking_history_not current'
]

@app.route('/predict_heart', methods=['POST'])
def predict_heart():
    try:
        data = request.get_json()
        print('Received heart data:', data)
        input_data = [float(data[feat]) for feat in heart_feature_order]
        input_array = np.array([input_data])

        numerical_indices = [0, 3, 4, 7, 9]
        input_array[:, numerical_indices] = heart_scaler.transform(input_array[:, numerical_indices])

        prediction = heart_model.predict(input_array)[0]
        probability = heart_model.predict_proba(input_array)[0][1]
        response = {'prediction': int(prediction), 'probability': float(probability)}
        print('Heart response:', response)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/predict_stroke', methods=['POST'])
def predict_stroke():
    try:
        data = request.get_json()
        print('Received stroke data:', data)

        # Convert raw input to one-hot encoded format
        input_data = [
            float(data['age']),
            float(data['hypertension']),
            float(data['heart_disease']),
            float(data['avg_glucose_level']),
            float(data['bmi']),
            # Gender
            1 if data['sex'] == 'male' else 0,      # gender_Male
            1 if data['sex'] == 'other' else 0,     # gender_Other (Female is reference: 0, 0)
            # Ever Married
            1 if data['ever_married'] == 'yes' else 0,  # ever_married_Yes (No is 0)
            # Work Type (Govt_job is reference: all 0s)
            1 if data['work_type'] == 'never_worked' else 0,  # work_type_Never_worked
            1 if data['work_type'] == 'private' else 0,       # work_type_Private
            1 if data['work_type'] == 'self-employed' else 0, # work_type_Self-employed
            1 if data['work_type'] == 'children' else 0,      # work_type_children
            # Residence Type
            1 if data['Residence_type'] == 'urban' else 0,    # Residence_type_Urban (Rural is 0)
            # Smoking Status (Unknown is reference: all 0s, but not in form; using Never as base if needed)
            1 if data['smoking_status'] == 'former' else 0,   # smoking_status_formerly smoked
            1 if data['smoking_status'] == 'never' else 0,    # smoking_status_never smoked
            1 if data['smoking_status'] == 'current' else 0   # smoking_status_smokes
        ]
        input_array = np.array([input_data])

        # Scale numerical features
        numerical_indices = [0, 3, 4]  # Indices of 'age', 'avg_glucose_level', 'bmi'
        input_array[:, numerical_indices] = stroke_scaler.transform(input_array[:, numerical_indices])

        # Predict
        prediction = stroke_model.predict(input_array)[0]
        probability = stroke_model.predict_proba(input_array)[0][1]
        response = {'prediction': int(prediction), 'probability': float(probability)}
        print('Stroke response:', response)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/predict_diabetes', methods=['POST'])
def predict_diabetes():
    try:
        data = request.get_json()
        print('Received diabetes data:', data)

        # Convert raw input to one-hot encoded format
        input_data = [
            float(data['age']),
            float(data['hypertension']),
            float(data['heart_disease']),
            float(data['bmi']),
            float(data['HbA1c_level']),
            float(data['blood_glucose_level']),
            1 if data['sex'] == 'male' else 0,
            1 if data['sex'] == 'other' else 0,
            1 if data['smoking_history'] == 'current' else 0,
            1 if data['smoking_history'] == 'ever' else 0,
            1 if data['smoking_history'] == 'former' else 0,
            1 if data['smoking_history'] == 'never' else 0,
            1 if data['smoking_history'] == 'not current' else 0
        ]
        input_array = np.array([input_data])

        # Scale numerical features
        numerical_indices = [0, 3, 4, 5]
        input_array[:, numerical_indices] = diabetes_scaler.transform(input_array[:, numerical_indices])

        # Convert to DMatrix for XGBoost
        dmatrix_input = xgb.DMatrix(input_array, feature_names=diabetes_feature_order)

        # Predict
        prediction = diabetes_model.predict(dmatrix_input)[0]
        probability = diabetes_model.predict(dmatrix_input)[0]  # XGBoost returns probabilities directly
        prediction_binary = 1 if prediction > 0.5 else 0
        response = {'prediction': int(prediction_binary), 'probability': float(prediction)}
        print('Diabetes response:', response)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)