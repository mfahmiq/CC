import os
from google.cloud import storage, firestore
import tensorflow as tf
from flask import Flask, request, jsonify
from keras.models import load_model
import numpy as np
from keras.applications.mobilenet_v2 import preprocess_input
from PIL import Image
import io
import datetime

app = Flask(__name__)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ML-API2.json'

storage_client = storage.Client()
bucket_name = 'recycleme-str'
bucket = storage_client.bucket(bucket_name)

# Function to initialize Firestore client
def initialize_firestore():
    return firestore.Client()

db = initialize_firestore()

def req(y_true, y_pred):
    req = tf.metrics.req(y_true, y_pred)[1]
    tf.keras.backend.get_session().run(tf.local_variables_initializer())
    return req

model = load_model('Recycleme-Model.h5', custom_objects={'req': req})

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_prediction(file):
    try:
        if not file or not allowed_file(file.filename):
            return {'message': 'No valid file uploaded', 'error': True}

        blob = bucket.blob(file.filename)
        blob.upload_from_string(file.read(), content_type=file.content_type)
        file.seek(0)

        img = Image.open(file.stream)
        img = img.resize((224, 224))
        x = np.array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        images = np.vstack([x])

        pred_sampah = model.predict(images)
        max_pred = pred_sampah.max()

        confidence_percent = f"{round(max_pred * 100)}%"

        categories = ['Limbah B3', 'Limbah Organik', 'Recycle', 'Limbah Residu']
        predicted_category = categories[np.argmax(pred_sampah)]

        if max_pred <= 0.75:
            return {'message': 'Sampah tidak terdeteksi', 'error': True}

        response_message = {
            'Limbah B3': 'Limbah ini termasuk Bahan Berbahaya dan Beracun. Harap Buang sesuai prosedur khusus di fasilitas pengelolaan limbah berbahaya.',
            'Limbah Organik': 'Limbah ini dapat dijadikan kompos. Mohon buanglah sampah ini di tempat kompos atau diolah menjadi pupuk alam.',
            'Recycle': 'Limbah ini dapat didaur ulang. Ditunggu kedatangannya di pusat daur ulang terdekat.',
            'Limbah Residu': 'Limbah ini tidak dapat didaur ulang. Mohon buanglah sampah ini di tempat sampah residu yang telah disediakan.'
        }

        result = {
            "category": predicted_category,
            "confidence": confidence_percent,
            "message": response_message[predicted_category],
            "storage_url": blob.public_url,
            "error": False
        }

        return result

    except Exception as e:
        return {'message': 'Error processing image', 'error': str(e)}

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'message': 'No image part'}), 400
    file = request.files['image']
    result = handle_prediction(file)
    if not result['error']:
        try:
            save_prediction(file.filename, result['category'], result['confidence'], result['message'], result['storage_url'])
        except Exception as e:
            print(f'Error saving to Firestore: {e}')
            return jsonify({'message': 'Error saving to Firestore', 'error': str(e)}), 500
    return jsonify(result)

@app.route('/history', methods=['GET'])
def get_predictions():
    try:
        collection_name = 'predictions'
        docs = db.collection(collection_name).stream()
        predictions = []
        for doc in docs:
            prediction = doc.to_dict()
            prediction['id'] = doc.id
            predictions.append(prediction)
        print(f'Retrieved {len(predictions)} predictions')
        return jsonify(predictions), 200
    except Exception as e:
        print(f'Error getting predictions: {e}')
        return jsonify({'message': 'Error getting predictions', 'error': str(e)}), 500

@app.route('/predictions/<id>', methods=['DELETE'])
def delete_prediction(id):
    try:
        collection_name = 'predictions'
        doc_ref = db.collection(collection_name).document(id)
        # Cek apakah dokumen ada sebelum menghapus
        if doc_ref.get().exists:
            doc_ref.delete()
            print(f'Deletion success: {id}')
            return jsonify({'message': f'Prediction {id} deleted successfully'}), 200
        else:
            print(f'Deletion failed: Document {id} does not exist')
            return jsonify({'message': f'Prediction {id} does not exist'}), 404
    except Exception as e:
        print(f'Error deleting prediction {id}: {e}')
        return jsonify({'message': f'Error deleting prediction {id}', 'error': str(e)}), 500

def save_prediction(filename, category, confidence, message, storage_url):
    try:
        collection_name = 'predictions'
        doc_ref = db.collection(collection_name).document()  # Create a new document with Firestore
        doc_ref.set({
            'filename': filename,
            'category': category,
            'confidence': confidence,
            'message': message,
            'storage_url': storage_url,
            'timestamp': datetime.datetime.now().isoformat(),  # Add timestamp for tracking
        })
        print(f'Data saved to Firestore: {filename}, {category}, {confidence}, {message}, {storage_url}')
    except Exception as e:
        print(f'Error saving to Firestore: {e}')
        raise

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
