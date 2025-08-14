const videoUpload = document.getElementById('videoUpload');
const videoPreview = document.getElementById('videoPreview');
const analyzeButton = document.getElementById('analyzeButton');
const buttonText = document.getElementById('buttonText');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultSection = document.getElementById('resultSection');
const analysisResult = document.getElementById('analysisResult');

const myModal = document.getElementById('myModal');
const closeModalButton = document.getElementById('closeModalButton');
const modalOkButton = document.getElementById('modalOkButton');
const modalMessage = document.getElementById('modalMessage');

let videoFile = null;

function showModal(message) {
    modalMessage.textContent = message;
    myModal.style.display = 'flex';
}

closeModalButton.onclick = () => { myModal.style.display = 'none'; };
modalOkButton.onclick = () => { myModal.style.display = 'none'; };
window.onclick = (event) => { if (event.target == myModal) myModal.style.display = 'none'; };

videoUpload.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('video/')) {
		
        if (file.size > 50 * 1024 * 1024) {
            showModal('El archivo es demasiado grande. Máximo permitido: 50MB.');
            videoUpload.value = '';
            analyzeButton.disabled = true;
            return;
        }

        videoFile = file;
        videoPreview.src = URL.createObjectURL(file);
        videoPreview.classList.remove('hidden');
        analyzeButton.disabled = false;
        resultSection.classList.add('hidden');
        analysisResult.innerHTML = '';
    } else {
        showModal('Por favor, selecciona un archivo de video válido.');
        videoFile = null;
        videoPreview.classList.add('hidden');
        videoPreview.src = '';
        analyzeButton.disabled = true;
    }
});

analyzeButton.addEventListener('click', () => {
	
    if (!videoFile) {
        showModal('Por favor, sube un video primero.');
        return;
    }

    buttonText.textContent = 'Analizando...';
    loadingSpinner.classList.remove('hidden');
    analyzeButton.disabled = true;
    videoUpload.disabled = true;
    resultSection.classList.add('hidden');
    analysisResult.innerHTML = '';

    const formData = new FormData();
    formData.append('file', videoFile);

    fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
		//console.log("Respuesta del backend:", data);

        if (data.average_score !== undefined && data.label) {
            const averageScore = data.average_score;
            const label = data.label;

            if (label === "Fake") {
                analysisResult.innerHTML = `
                    <p class="text-xl font-bold text-red-600">Posible video generado por IA</p>
                    <p class="text-lg">Probabilidad estimada: ${averageScore}%</p>`;
            } else {
                analysisResult.innerHTML = `
                    <p class="text-xl font-bold text-green-600">Parece ser un video real</p>
                    <p class="text-lg text-gray-600">El modelo no detectó señales fuertes de generación por IA</p>`;
            }

            resultSection.classList.remove('hidden');
            showModal('El análisis ha finalizado correctamente.');
        } else {
            showModal('Error: No se pudo obtener el resultado del análisis.');
        }
    })
    .catch(err => {
        console.error(err);
        showModal('Error al analizar el video. Ver consola para más detalles.');
    })
    .finally(() => {
        buttonText.textContent = 'Analizar Video';
        loadingSpinner.classList.add('hidden');
        analyzeButton.disabled = false;
        videoUpload.disabled = false;
    });
});