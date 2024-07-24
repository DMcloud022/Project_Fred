import os
import io
import qrcode
from groq import Groq
from docx import Document
from email import message_from_string
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from flask import Blueprint, render_template, request, send_file, jsonify, abort
from flask_login import login_required
from werkzeug.utils import secure_filename
from .config import Config
from .functions import process_input, create_pdf_report, analyze_input, generate_development_process

# Initialize Groq client
groq_client = Groq(api_key=Config.GROQ_API_KEY)

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        input_text = ''
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_extension = os.path.splitext(filename)[1].lower()
                input_text = process_input(file, file_extension)
            else:
                return jsonify({'error': 'Invalid file type'}), 400
        elif 'text' in request.form:
            input_text = request.form['text']
        else:
            return jsonify({'error': 'No input provided'}), 400

        if not input_text:
            return jsonify({'error': 'Empty input'}), 400

        try:
            requirements = analyze_input(input_text)
            development_process = generate_development_process(requirements)

            return jsonify({
                'requirements': requirements,
                'development_process': development_process
            })
        except Exception as e:
            return jsonify({'error': f'Error processing input: {str(e)}'}), 500

    return render_template('index.html')

@main.route('/analyze', methods=['POST'])
@login_required
def analyze():
    try:
        input_text = ''
        if 'input_type' in request.form and request.form['input_type'] == 'file':
            file = request.files['file']
            if not file:
                return jsonify({'error': 'No file uploaded'}), 400
            filename = secure_filename(file.filename)
            file_extension = os.path.splitext(filename)[1].lower()
            input_text = process_input(file, file_extension)
        elif 'input_text' in request.form:
            input_text = request.form['input_text']
        else:
            return jsonify({'error': 'Invalid input type'}), 400

        if not input_text:
            return jsonify({'error': 'Empty input'}), 400

        requirements = analyze_input(input_text)
        development_process = generate_development_process(requirements)
        
        return jsonify({
            'requirements': requirements,
            'development_process': development_process
        })
    except Exception as e:
        return jsonify({'error': f'Error analyzing input: {str(e)}'}), 500


@main.route('/preview', methods=['POST'])
@login_required
def preview():
    # Render a preview of the development process
    development_process = request.form.get('development_process')
    if not development_process:
        abort(400, description="No development process provided")
    return render_template('preview.html', content=development_process)

@main.route('/download', methods=['POST'])
@login_required
def download():
    # Generate and send a PDF report of the development process
    development_process = request.form.get('development_process')
    if not development_process:
        abort(400, description="No development process provided")
    try:
        pdf_buffer = create_pdf_report(development_process)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name='development_process.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        abort(500, description=f"Error creating PDF: {str(e)}")
