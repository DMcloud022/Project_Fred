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
from .config import Config

# Initialize Groq client
groq_client = Groq(api_key=Config.GROQ_API_KEY)

def process_input(file, file_extension):
    # Process different file types and extract text content
    if file_extension == '.txt':
        return file.read().decode('utf-8', errors='ignore')
    elif file_extension == '.docx':
        doc = Document(file)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    elif file_extension in ['.eml', '.msg']:
        email_content = file.read().decode('utf-8', errors='ignore')
        email_message = message_from_string(email_content)
        return email_message.get_payload()
    else:
        raise ValueError("Unsupported file type")

def analyze_input(input_text):
    # Truncate the input text if it's too long
    max_length = 4096  # Adjust this based on the model's context size
    if len(input_text) > max_length:
        input_text = input_text[:max_length]
    
    # Analyze input text to generate project requirements
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Analyze the following input and generate project requirements: {input_text}",
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def generate_development_process(requirements):
    # Truncate the requirements if they are too long
    max_length = 4096  # Adjust this based on the model's context size
    if len(requirements) > max_length:
        requirements = requirements[:max_length]
    
    # Generate a development process based on project requirements
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Based on these project requirements, outline the overall system development process, following best practices and internationally recognized standards, from gathering requirements from stakeholders to deployment and maintenance. Use established methodologies such as iterative or agile development, requirements engineering, and testing frameworks. Provide recommendations for each stage of the development lifecycle, including requirements gathering, design, implementation, testing, and deployment. Additionally, please summarize the project's key aspects, make predictions for future improvements and challenges that may be faced, and suggest solutions to overcome them. Format the response in a step-by-step process, ensuring clarity and concision. Focus on providing a comprehensive overview of the development lifecycle, highlighting essential considerations and best practices throughout the journey. Requirements: {requirements}",
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content


def create_pdf_report(content):
    # Create a PDF report from the provided content
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    title = Paragraph("Project Development Process", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    for line in content.split('\n'):
        p = Paragraph(line, styles['Normal'])
        story.append(p)
        story.append(Spacer(1, 6))

    # Generate and add QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(content)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img_buffer = io.BytesIO()
    qr_img.save(qr_img_buffer)
    qr_img_buffer.seek(0)
    qr_image = Image(qr_img_buffer, width=2*inch, height=2*inch)
    story.append(qr_image)

    doc.build(story)
    buffer.seek(0)
    return buffer
