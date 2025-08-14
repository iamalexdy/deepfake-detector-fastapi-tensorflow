from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


import os
import shutil
import cv2
import numpy as np
import glob

from tensorflow.keras.applications import Xception
from tensorflow.keras.applications.xception import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D

# === Inicialización FastAPI ===
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Se puede restringir esto al puerto usado, ejem: ["http://localhost:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carpetas necesarias
os.makedirs("uploaded_videos", exist_ok=True)
os.makedirs("frames", exist_ok=True)

# Montar carpeta estática
app.mount("/static", StaticFiles(directory="frames"), name="static")

# === Cargar modelo Xception (preentrenado en ImageNet, adaptado a binario) ===
print("Cargando modelo Xception...")
base_model = Xception(weights="imagenet", include_top=False)
x = GlobalAveragePooling2D()(base_model.output)
preds = Dense(1, activation="sigmoid")(x)
model = Model(inputs=base_model.input, outputs=preds)

# Congelar capas base
for layer in base_model.layers:
    layer.trainable = False
print("Modelo cargado correctamente (usando pesos ImageNet).")

# === Funciones auxiliares ===
def extract_frames(video_path, interval=1):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    count, saved = 0, 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count % (fps * interval) == 0:
            filename = f"frames/frame_{saved:03d}.jpg"
            cv2.imwrite(filename, frame)
            saved += 1
        count += 1
    cap.release()
    return saved

def limpiar_archivos():
    for f in glob.glob("frames/*.jpg"):
        os.remove(f)
    for v in glob.glob("uploaded_videos/*.mp4"):
        os.remove(v)

def predict_frame(frame_path):
    img = image.load_img(frame_path, target_size=(299, 299))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    prediction = model.predict(img_array)[0][0]
    return prediction  # 0=real, 1=fake (aunque está preentrenado en ImageNet)

# === Endpoint principal ===
@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    video_path = f"uploaded_videos/{file.filename}"
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    total_frames = extract_frames(video_path, interval=1)

    predictions = []
    for i in range(total_frames):
        frame_path = f"frames/frame_{i:03d}.jpg"
        score = predict_frame(frame_path)
        predictions.append(score)

    median_score = float(np.median(predictions))
    label = "Fake" if median_score > 0.5 else "Real"
    probability = round(median_score * 100, 2)

    limpiar_archivos()
    
    print({
    "label": label,
    "average_score": probability,
    "message": "Parece ser un video generado por IA" if label == "Fake" else "Parece ser un video real"
    })

    return JSONResponse(content={
        "label": label,
        "average_score": probability,
        "message": "Parece ser un video generado por IA" if label == "Fake" else "Parece ser un video real"
    })

