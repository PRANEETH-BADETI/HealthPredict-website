// Toggle menu for mobile
function toggleMenu() {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('show');
}

// Switch between tabs
function switchTab(tabId) {
    document.querySelectorAll('.form-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(button => button.classList.remove('active'));
    document.getElementById(tabId + '-form').classList.add('active');
    const buttons = document.querySelectorAll('.tab');
    for (let btn of buttons) {
        if (btn.getAttribute('onclick').includes(tabId)) {
            btn.classList.add('active');
            break;
        }
    }
}

// Activate a specific tab from another section
function activateTab(tabId) {
    switchTab(tabId);
    document.getElementById('predict').scrollIntoView({ behavior: 'smooth' });
}

// Helper function to send prediction request
async function sendPrediction(endpoint, data, resultElement, predictionTextElement) {
    try {
        console.log('Sending data to endpoint:', endpoint, data);
        const response = await fetch(`https://healthpredict-mmjr.onrender.com/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server returned ${response.status}: ${errorText}`);
        }

        const result = await response.json();
        console.log('Response data:', result);

        if (result.prediction === 1) {
            resultElement.className = 'prediction-result high-risk';
            predictionTextElement.innerHTML = `<strong>Higher Risk:</strong> Probability: ${(result.probability * 100).toFixed(2)}%. Consult a healthcare professional.`;
        } else {
            resultElement.className = 'prediction-result low-risk';
            predictionTextElement.innerHTML = `<strong>Lower Risk:</strong> Probability: ${(result.probability * 100).toFixed(2)}%. Maintain a healthy lifestyle.`;
        }
        resultElement.style.display = 'block';
    } catch (error) {
        console.error('Fetch error:', error.message);
        predictionTextElement.innerHTML = `An error occurred: ${error.message}. Please try again.`;
        resultElement.style.display = 'block';
    }
}

// Stroke prediction
function predictStroke(event) {
    event.preventDefault();
    const data = {
        age: parseFloat(document.getElementById('stroke-age').value),
        sex: document.getElementById('stroke-sex').value,
        hypertension: document.getElementById('stroke-hypertension').value === 'yes' ? 1 : 0,
        heart_disease: document.getElementById('stroke-heart-disease').value === 'yes' ? 1 : 0,
        avg_glucose_level: parseFloat(document.getElementById('stroke-glucose').value),
        bmi: parseFloat(document.getElementById('stroke-bmi').value),
        ever_married: document.getElementById('stroke-ever-married').value,
        work_type: document.getElementById('stroke-work-type').value,
        Residence_type: document.getElementById('stroke-residence').value,
        smoking_status: document.getElementById('stroke-smoking').value
    };
    sendPrediction('predict_stroke', data, document.getElementById('stroke-result'), document.getElementById('stroke-prediction-text'));
}

// Heart disease prediction (unchanged)
function predictHeart(event) {
    event.preventDefault();
    const data = {
        age: parseFloat(document.getElementById('heart-age').value),
        sex: document.getElementById('heart-sex').value === 'male' ? 1 : 0,
        'chest pain type': document.getElementById('heart-cp').value === 'typical' ? 3 : (document.getElementById('heart-cp').value === 'atypical' ? 2 : (document.getElementById('heart-cp').value === 'non-anginal' ? 1 : 0)),
        'resting bp s': parseFloat(document.getElementById('heart-trestbps').value),
        cholesterol: parseFloat(document.getElementById('heart-chol').value),
        'fasting blood sugar': document.getElementById('heart-fbs').value === 'yes' ? 1 : 0,
        'resting ecg': parseInt(document.getElementById('heart-resting-ecg').value),
        'max heart rate': parseFloat(document.getElementById('heart-max-hr').value),
        'exercise angina': document.getElementById('heart-ex-angina').value === 'yes' ? 1 : 0,
        oldpeak: parseFloat(document.getElementById('heart-oldpeak').value),
        'ST slope': parseInt(document.getElementById('heart-st-slope').value)
    };
    sendPrediction('predict_heart', data, document.getElementById('heart-result'), document.getElementById('heart-prediction-text'));
}

// Diabetes prediction (unchanged)
function predictDiabetes(event) {
    event.preventDefault();
    const data = {
        age: parseFloat(document.getElementById('diabetes-age').value),
        sex: document.getElementById('diabetes-sex').value,
        hypertension: document.getElementById('diabetes-hypertension').value === 'yes' ? 1 : 0,
        heart_disease: document.getElementById('diabetes-heart-disease').value === 'yes' ? 1 : 0,
        bmi: parseFloat(document.getElementById('diabetes-bmi').value),
        HbA1c_level: parseFloat(document.getElementById('diabetes-hba1c').value),
        blood_glucose_level: parseFloat(document.getElementById('diabetes-glucose').value),
        smoking_history: document.getElementById('diabetes-smoking').value
    };
    sendPrediction('predict_diabetes', data, document.getElementById('diabetes-result'), document.getElementById('diabetes-prediction-text'));
}

// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth' });
        });
    });

    document.getElementById('strokeForm').addEventListener('submit', predictStroke);
    document.getElementById('heartForm').addEventListener('submit', predictHeart);
    document.getElementById('diabetesForm').addEventListener('submit', predictDiabetes);
});