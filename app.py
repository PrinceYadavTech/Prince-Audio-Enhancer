@app.route('/process', methods=['POST'])
def process_audio():
    try:
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        # File ko upload folder mein save karna
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Process the audio using the full_audio_edit function
        processed_file_name = 'processed_file.mp3'
        processed_file_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_file_name)

        full_audio_edit(file_path, processed_file_path)

        # Return the download link
        return render_template('index.html', download_link=processed_file_name)

    except Exception as e:
        # Log the error in detail and show it on the server log
        app.logger.error(f"Error processing audio: {e}")
        return f"Error processing audio: {e}", 500  # Return 500 Internal Server Error  
