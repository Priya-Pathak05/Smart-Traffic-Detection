from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from ultralytics import YOLO

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

model = YOLO('yolov8n.pt')  # Replace with your model if custom

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allocate_time(vehicle_count):
    if vehicle_count <= 5:
        return 10
    elif 6 <= vehicle_count <= 15:
        return 30
    else:
        return 60

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)

        # Run detection
        results = model(upload_path)
        result_filename = f"detected_{filename}"
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
        results[0].save(filename=result_path)

        # Count detected vehicles (or all objects if general model)
        vehicle_count = len(results[0].boxes)
        allocated_time = allocate_time(vehicle_count)

        result_text = f"Detected {vehicle_count} object(s) in traffic image."
        time_text = f"⏱️ Allocated green light time: {allocated_time} seconds"

        return render_template('result.html',
                               image_path=result_filename,
                               result=result_text,
                               time_allocated=time_text)

    return "File type not allowed", 400

if __name__ == '__main__':
    app.run(debug=True)
