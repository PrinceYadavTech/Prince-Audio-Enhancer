from flask import Flask, request, render_template, send_from_directory
import os
from pydub import AudioSegment, silence, effects

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

# Ensure the processed folder exists
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Simplified audio processing function
def full_audio_edit(input_file, output_file, silence_thresh=-40, min_silence_len=500):
    # Step 1: Load audio
    audio = AudioSegment.from_file(input_file, format="mp3")

    # Step 2: Remove silence
    chunks = silence.split_on_silence(audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )
    audio = AudioSegment.empty()
    for chunk in chunks:
        audio += chunk + AudioSegment.silent(duration=150)  # natural pause

    # Step 3: Normalize
    audio = effects.normalize(audio)

    # Step 4: Speed increase by 2%
    audio = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * 1.02)
    }).set_frame_rate(audio.frame_rate)

    # Step 5: Set sample rate to 16000 Hz
    audio = audio.set_frame_rate(16000)

    # Step 6: Convert to mono
    audio = audio.set_channels(1)

    # Step 7: Final normalize
    audio = effects.normalize(audio)

    # Step 8: Export the final audio
    audio.export(output_file, format="mp3")
    print("✅ Final audio saved as:", output_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # File ko upload folder mein save karna
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Process the audio using the full_audio_edit function
    try:
        # Processed file path
        processed_file_name = 'processed_file.mp3'
        processed_file_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_file_name)

        # Call full_audio_edit to process the uploaded file
        full_audio_edit(file_path, processed_file_path)

        # Return the download link
        return render_template('index.html', download_link=processed_file_name)

    except Exception as e:
        return f"Error processing audio: {e}"

# Serve processed file from the processed folder
@app.route('/processed/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
