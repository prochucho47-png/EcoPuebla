// Mostrar la vista previa de la imagen seleccionada o capturada
document.getElementById('imageInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const dropText = document.getElementById('fileDropText');
        if (dropText) {
            dropText.textContent = 'Imagen seleccionada: ' + file.name;
        }
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('imagePreview');
            preview.src = e.target.result;
            preview.style.display = 'block';
            document.getElementById('result-section').style.display = 'none'; // Ocultar resultados anteriores
        };
        reader.readAsDataURL(file);
    }
});

// Enviar la imagen al backend al dar click en Analizar
document.getElementById('analyzeBtn').addEventListener('click', function() {
    const fileInput = document.getElementById('imageInput');
    
    if (fileInput.files.length === 0) {
        alert('Por favor, toma una foto o selecciona una imagen primero.');
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.textContent = 'Analizando en el servidor...';
    analyzeBtn.disabled = true;

    const sendData = async (fd) => {
        try {
            const response = await fetch('/api/recognize', {
                method: 'POST',
                body: fd
            });

            const result = await response.json();

            if (result.success) {
                const data = result.data;
                const resultContent = document.getElementById('resultContent');
                
                resultContent.innerHTML = `
                    <p><strong>Clasificación:</strong> ${data.tipo}</p>
                    <p><strong>Nombre Común:</strong> ${data.nombre_comun}</p>
                    <p><strong>Nombre Científico:</strong> <em>${data.nombre_cientifico}</em></p>
                    <p><strong>Descripción:</strong> ${data.descripcion}</p>
                    <p><strong>Fiabilidad de IA:</strong> ${(data.confianza * 100).toFixed(1)}%</p>
                `;
                document.getElementById('result-section').style.display = 'block';
            } else {
                alert('Error en el análisis: ' + result.error);
            }
        } catch (error) {
            console.error('Error al contactar con la API:', error);
            alert('Ocurrió un error al intentar comunicarse con el servidor.');
        } finally {
            analyzeBtn.textContent = 'Analizar Imagen';
            analyzeBtn.disabled = false;
        }
    };

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                formData.append('lat', position.coords.latitude);
                formData.append('lng', position.coords.longitude);
                sendData(formData);
            },
            (error) => {
                console.warn('No se pudo obtener ubicación GPS:', error);
                sendData(formData);
            },
            { timeout: 5000 }
        );
    } else {
        sendData(formData);
    }
});
