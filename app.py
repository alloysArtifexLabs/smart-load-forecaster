from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Initialize FastAPI app
app = FastAPI(
    title="Smart Load Forecaster API",
    description="API for predicting energy consumption using a trained LSTM model.",
    version="1.0.0"
)

# Load the model and scaler
model = load_model("models/smart_load_forecaster_model.h5", compile=False)


with open('models/scaler.save', 'rb') as f:
    scaler = joblib.load("models/scaler.save")

# Define input data schema
class ConsumptionData(BaseModel):
    recent_consumption: list  # List of recent consumption values (e.g., last 30 days)

@app.post("/predict")
async def predict_energy(data: ConsumptionData):
    try:
        # Validate input length
        if len(data.recent_consumption) != 30:
            raise HTTPException(status_code=400, detail="Please provide exactly 30 recent consumption values.")

        # Convert input data to numpy array and reshape for model
        input_data = np.array(data.recent_consumption).reshape(-1, 1)

        # Normalize the data
        input_scaled = scaler.transform(input_data)

        # Reshape for LSTM model [samples, timesteps, features]
        input_scaled = input_scaled.reshape(1, 30, 1)

        # Make prediction
        prediction_scaled = model.predict(input_scaled)

        # Inverse transform the prediction to get the actual value
        prediction = scaler.inverse_transform(prediction_scaled)

        return {
            "predicted_energy_consumption_kWh": float(prediction[0][0])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Load Forecaster API 🚀"}
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
