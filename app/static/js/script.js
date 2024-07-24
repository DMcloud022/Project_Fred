document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysis-form');
    const resultsDiv = document.getElementById('results');
    const requirementsDiv = document.getElementById('requirements');
    const developmentProcessDiv = document.getElementById('development-process');
    const previewBtn = document.getElementById('preview-btn');
    const downloadBtn = document.getElementById('download-btn');
    const inputTypeSelect = document.getElementById('input_type');
    const textInput = document.getElementById('text_input');
    const fileInput = document.getElementById('file_input');

    inputTypeSelect.addEventListener('change', function() {
        if (this.value === 'text') {
            textInput.style.display = 'block';
            fileInput.style.display = 'none';
        } else {
            textInput.style.display = 'none';
            fileInput.style.display = 'block';
        }
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);

        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            requirementsDiv.innerHTML = '<h3>Requirements:</h3><p>' + data.requirements + '</p>';
            developmentProcessDiv.innerHTML = '<h3>Development Process:</h3><p>' + data.development_process + '</p>';
            resultsDiv.style.display = 'block';
        })
        .catch(error => console.error('Error:', error));
    });

    previewBtn.addEventListener('click', function() {
        const developmentProcess = developmentProcessDiv.innerText;
        const form = document.createElement('form');
        form.method = 'post';
        form.action = '/preview';

        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'development_process';
        input.value = developmentProcess;

        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    });

    downloadBtn.addEventListener('click', function() {
        const developmentProcess = developmentProcessDiv.innerText;
        const form = document.createElement('form');
        form.method = 'post';
        form.action = '/download';

        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'development_process';
        input.value = developmentProcess;

        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    });
});