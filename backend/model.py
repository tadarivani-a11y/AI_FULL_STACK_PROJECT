import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FILE = os.path.join(BASE_DIR, "data", "traffic_data.csv")
MODEL_FILE = os.path.join(BASE_DIR, "backend", "traffic_model.pkl")

FEATURES = ["vehicles", "hour", "day", "weather"]


def train_model():
    data = pd.read_csv(DATA_FILE)

    X = data[FEATURES]
    y = data["traffic"]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model.fit(X, y)

    joblib.dump(model, MODEL_FILE)

    print("AI model trained successfully!")

    return model


def get_model():
    if not os.path.exists(MODEL_FILE):
        return train_model()

    return joblib.load(MODEL_FILE)


def predict_traffic(vehicles, hour, day, weather):
    model = get_model()

    prediction = model.predict(
        [[vehicles, hour, day, weather]]
    )[0]

    prediction = max(0, min(100, prediction))

    return float(prediction)