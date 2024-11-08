from fastapi import FastAPI
from google.cloud import storage
import requests
import os
import json
from datetime import datetime

app = FastAPI()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] ="/workspaces/api/utopian-honor-438417-u7-5b7f84fcfd25.json"
# Configuración de Google Cloud
PROJECT_ID = 'utopian-honor-438417-u7'
BUCKET_NAME = 'etl_agu'
API_KEY = 'AIzaSyDDt1fiH2cTopWMX_qfg50nm0taKg4egV4'
PLACE_IDS = [
    'ChIJOwg_06VPwokRYv534QaPC8g'
]
#, 'ChIJ7cv00DwsDogRAMDACa2m4K8',
#   'ChIJE9on3F3HwoAR9AhGJW_fL-I', 'ChIJ60u11Ni3xokRwVg-jNgU9Yk',
#   'ChIJrw7QBK9YXIYRvBagEDvhVgg', 'ChIJS5dFe_cZTIYRj2dH9qSb7Lk',
#   'ChIJ0X31pIK3voARo3mz1ebVzDo', 'ChIJEcHIDqKw2YgRZU-t3XHylv8'

# Inicializa el cliente de Google Cloud Storage
storage_client = storage.Client()

@app.get("/fetch-places-data")
def fetch_places_data():
    results = []
    for place_id in PLACE_IDS:
        response = requests.get(
            f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEY}"
        )
        
        if response.status_code == 200:
            place_data = response.json().get("result", {})
            results.append(place_data)
            save_to_gcs(place_data, place_id)
        else:
            return {"error": f"Failed to fetch data for place_id: {place_id}"}

    return {"status": "Data fetched and uploaded to Google Cloud Storage", "data": results}

def save_to_gcs(data, place_id):
    # Genera un nombre único para el archivo JSON
    file_name = f"carga_inicial/API_{place_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    file_path = f"gs://{BUCKET_NAME}/{file_name}"
    
    # Convierte los datos a JSON y guarda en el bucket
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    blob.upload_from_string(
        data=json.dumps(data), 
        content_type='application/json'
    )
    print(f"Data for {place_id} saved to {file_path}")

