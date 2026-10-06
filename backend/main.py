from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pypdf import PdfReader
import io

from .database import init_db, save_prediction, get_predictions
from .model import predict_traffic, train_model
from .ai_assistant import TrafficAI


app = FastAPI(
    title="AI Smart Traffic Management",
    description="AI based traffic management system",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


init_db()

ai = TrafficAI()


class PredictionRequest(BaseModel):

    vehicles: int = Field(
        ge=0,
        le=1000
    )

    hour: int = Field(
        ge=0,
        le=23
    )

    day: int = Field(
        ge=1,
        le=7
    )

    weather: int = Field(
        ge=0,
        le=1
    )


class ChatRequest(BaseModel):

    question: str = Field(
        min_length=1,
        max_length=1000
    )


def classify_traffic(traffic):

    if traffic < 30:
        return "Low", 30

    elif traffic < 60:
        return "Medium", 50

    else:
        return "High", 80


@app.get("/")
def home():

    return {
        "message":
        "AI Smart Traffic Management API is running"
    }


@app.get("/api/health")
def health():

    return {
        "status": "OK"
    }


@app.post("/api/train")
def train():

    train_model()

    return {
        "message":
        "AI model trained successfully"
    }


@app.post("/api/predict")
def predict(request: PredictionRequest):

    traffic = predict_traffic(
        request.vehicles,
        request.hour,
        request.day,
        request.weather
    )

    congestion, signal_time = classify_traffic(
        traffic
    )

    save_prediction(
        request.vehicles,
        request.hour,
        request.day,
        request.weather,
        traffic,
        congestion,
        signal_time
    )

    return {
        "traffic": round(traffic, 2),
        "congestion": congestion,
        "signal_time": signal_time
    }


@app.get("/api/history")
def history():

    return get_predictions()


@app.post("/api/chat")
def chat(request: ChatRequest):

    answer = ai.ask(
        request.question
    )

    return {
        "answer": answer
    }


@app.post("/api/pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_data = await file.read()

    reader = PdfReader(
        io.BytesIO(file_data)
    )

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text

    chunks = []

    chunk_size = 800

    for i in range(
        0,
        len(text),
        chunk_size
    ):

        chunk = text[
            i:i + chunk_size
        ]

        if chunk.strip():
            chunks.append(chunk)

    if chunks:

        embeddings = ai.embedder.encode(
            chunks
        ).tolist()

        ai.collection.add(
            ids=[
                f"pdf_{i}"
                for i in range(len(chunks))
            ],
            documents=chunks,
            embeddings=embeddings
        )

    return {
        "filename": file.filename,
        "pages": len(reader.pages),
        "chunks": len(chunks)
    }