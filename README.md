# Detector de Videos IA - Xception

Este proyecto utiliza un modelo basado en Xception para analizar videos y determinar si pueden ser generados por IA (deepfake).

---

## Requisitos previos
- Tener instalado Python 3.8
- PowerShell (Windows)

---

## Pasos de instalación y ejecución

### 1. Crear entorno virtual con Python 3.8
```powershell
py -3.8 -m venv venv
```

### 2. Activar entorno virtual
```powershell
.
env\Scripts ctivate
```

### 3. Instalar dependencias necesarias
```powershell
pip install fastapi uvicorn tensorflow opencv-python numpy requests python-multipart pillow
```

### 4. Ejecutar el servidor
```powershell
uvicorn main:app --reload
```

### 5. Acceder a la aplicación
Abrir el navegador en:
```
http://127.0.0.1:8000 o abre el index.html
```

---

## Notas
- El modelo Xception se descargará automáticamente la primera vez que se ejecute.
- Recomendado usar videos cortos para un análisis más rápido.
