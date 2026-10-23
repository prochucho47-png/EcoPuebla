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
                
                const isFloraFauna = (data.tipo === 'Flora' || data.tipo === 'Fauna');
                const badgeColor = isFloraFauna ? '#2E7D32' : '#C62828';
                const badgeBg = isFloraFauna ? '#E8F5E9' : '#FFEBEE';
                const statusMessage = isFloraFauna 
                    ? `<span style="display:inline-block; background:${badgeBg}; color:${badgeColor}; padding:4px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; margin-bottom:10px;">${data.tipo} (Puntos otorgados)</span>`
                    : `<span style="display:inline-block; background:${badgeBg}; color:${badgeColor}; padding:4px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; margin-bottom:10px;">No es Flora ni Fauna (0 pts)</span>`;

                resultContent.innerHTML = `
                    <div style="margin-bottom: 8px;">${statusMessage}</div>
                    <p><strong>Objeto / Especie detectada:</strong> ${data.nombre_comun}</p>
                    ${data.nombre_cientifico && data.nombre_cientifico !== 'N/A' && data.nombre_cientifico !== '-' ? `<p><strong>Nombre Científico:</strong> <em>${data.nombre_cientifico}</em></p>` : ''}
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
