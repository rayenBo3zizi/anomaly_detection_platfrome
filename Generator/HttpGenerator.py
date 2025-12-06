
import requests
import json
from decouple import config, Config, RepositoryEnv
import os

class HTTPEnabledSensorSimulator:
    def __init__(self, base_url, token=None, farmer_id=None):
        self.base_url = base_url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}" if self.token else "",
            "Content-Type": "application/json"
        }
        self.plots = []
        

    def get_jwt_token(username, password):
        
        login_url = "http://127.0.0.1:8000/api/token/"
        
        response = requests.post(
            login_url,
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data['access']  # Token JWT
        else:
            print(f"❌ Erreur login: {response.text}")
            return None
        
    
    def fetch_plots(self):
        """Récupère tous les plots disponibles"""
        try:
            response = requests.get(
                f"{self.base_url}/api/fieldplots/",
                headers=self.headers
            )
            if response.status_code == 200:
                self.plots = response.json()
                print(f"✅ {len(self.plots)} plots récupérés")
                for plot in self.plots:
                    print(f"   - Plot {plot['id']}")
                return self.plots
            else:
                print(f"❌ Erreur: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return []
        
    def send_reading(self, plot_id, sensor_type, value):
        url = f"{self.base_url}/api/sensor-readings/"

        payload = {
            "plot": plot_id,
            "sensor_type": sensor_type,
            "value": float(value),
            "source": "simulator"
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)

            if response.status_code in (200, 201):
                print(f"✔ Sent {sensor_type}={value} for plot {plot_id}")
            else:
                print(f"❌ ERROR {response.status_code}: {response.text}")

        except Exception as e:
            print("❌ POST error:", e)



