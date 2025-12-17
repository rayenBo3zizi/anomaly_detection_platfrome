import time
import random
from datetime import datetime, timedelta
import numpy as np


class CleanSensorSimulator:
    def __init__(
        self,
        plot_id=1,
        scenario=None,
        seed=None,
        fast_simulate=False,
        sim_speed_factor=1,
        cross_effects=False,
    ):
        self.plot_id = plot_id
        self.current_time = datetime.now()
        self.fast_simulate = fast_simulate
        self.sim_speed_factor = sim_speed_factor
        self.cross_effects = cross_effects

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)


        self.current_temperature = random.uniform(20, 26)
        self.current_humidity = random.uniform(55, 70)
        self.current_soil_moisture = random.uniform(55, 70)

        self.base_temperature = 23.0
        self.base_humidity = 60.0
        self.base_soil_moisture = 65.0

        # Drift
        self.drift_temp = 0.0
        self.drift_hum = 0.0
        self.drift_soil = 0.0
        self.drift_rate = 0.005  

        # Irrigation
        self.last_irrigation = self.current_time - timedelta(hours=12)
        self.irrigation_interval = random.uniform(12, 24) * 3600

        
        self.normal_duration = 15 * 60        # 15 minutes en mode normal
        self.anomaly_duration = 10 * 60       # 10 minutes d'anomalie
        self.recovery_duration = 5 * 60       # 5 minutes de récupération

        # Modes
        self.mode = "normal"
        self.mode_start = self.current_time
        self.recovery_targets = None

        # Anomalies
        self.anomaly_list = [
            "temp_spike",
            "temp_low",
            "humidity_spike",
            "humidity_drop",
            "moisture_drop",
            "moisture_leak"
        ]

        # Script scenario
        self.scenario = scenario or []
        self.scenario_index = 0

        # Storage for plotting
        self.timestamps = []
        self.temps = []
        self.humids = []
        self.moistures = []

    def advance_time(self, interval):
        if self.fast_simulate:
            self.current_time += timedelta(seconds=interval * self.sim_speed_factor)
        else:
            time.sleep(interval)
            self.current_time = datetime.now()

    def apply_drift(self):
        self.drift_temp += random.uniform(-self.drift_rate, self.drift_rate)
        self.drift_hum += random.uniform(-self.drift_rate, self.drift_rate)
        self.drift_soil += random.uniform(-self.drift_rate, self.drift_rate)

        self.drift_temp = np.clip(self.drift_temp, -0.2 * self.base_temperature, 0.2 * self.base_temperature)
        self.drift_hum = np.clip(self.drift_hum, -0.2 * self.base_humidity, 0.2 * self.base_humidity)
        self.drift_soil = np.clip(self.drift_soil, -0.2 * self.base_soil_moisture, 0.2 * self.base_soil_moisture)

    def check_irrigation(self):
        elapsed_since_irr = (self.current_time - self.last_irrigation).total_seconds()
        if elapsed_since_irr >= self.irrigation_interval:
            increase = random.uniform(15, 25)
            self.current_soil_moisture = min(75, self.current_soil_moisture + increase)
            self.last_irrigation = self.current_time
            self.irrigation_interval = random.uniform(12, 24) * 3600
            print(f"\n*** IRRIGATION simulée: +{increase:.2f}% sol ***\n")

    def get_diurnal_targets(self):
        hour = self.current_time.hour + self.current_time.minute / 60.0
        
        # TEMPÉRATURE: cycle sinusoïdal avec pic à 15h (heure 15)
        # sin(0) = 0 à minuit, sin(π/2) = 1 à 6h du matin (minimum)
        # On décale pour avoir le max à 15h
        temp_phase = (hour - 6) / 24 * 2 * np.pi  # Décalage pour min à 6h
        temp_amplitude = 5.0  # Variation de ±5°C
        target_temp = self.base_temperature + temp_amplitude * np.sin(temp_phase)
        
        # HUMIDITÉ: corrélation INVERSE forte avec température
        # Quand temp augmente, humidité baisse
        hum_amplitude = 10.0  # Variation de ±10%
        target_hum = self.base_humidity - 0.8 * temp_amplitude * np.sin(temp_phase)
        # Ajout de bruit réaliste
        target_hum += random.uniform(-2, 2)
        
        # SOL: décroissance graduelle pendant la journée (évapotranspiration)
        # Plus rapide quand il fait chaud (jour) vs nuit
        hours_since_irrigation = (self.current_time - self.last_irrigation).total_seconds() / 3600
        
        # Décroissance dépendante de l'heure: plus rapide entre 10h-18h
        if 10 <= hour <= 18:
            soil_decrease_rate = 0.15  # %/heure pendant la journée
        else:
            soil_decrease_rate = 0.05  # %/heure pendant la nuit
        
        # Calcul de la cible du sol
        target_soil = self.base_soil_moisture - (soil_decrease_rate * hours_since_irrigation)
        target_soil = max(45, target_soil)  # Ne pas descendre sous 45%

        return target_temp, target_hum, target_soil

    def switch_mode_if_needed(self):
        now = self.current_time
        elapsed = (now - self.mode_start).total_seconds()

        
        if self.scenario_index < len(self.scenario):
            start_time, anomaly_type, duration = self.scenario[self.scenario_index]
            if now >= start_time and self.mode == "normal":
                self.mode = anomaly_type
                self.anomaly_duration = duration
                self.mode_start = now
                self.scenario_index += 1
                print(f"\n*** ANOMALIE SCRIPTÉE déclenchée: {self.mode} ***\n")
                return

        
        if self.mode == "normal" and elapsed >= self.normal_duration:
            self.mode = random.choice(self.anomaly_list)
            self.mode_start = now
            print(f"\n*** ANOMALIE déclenchée: {self.mode} ***\n")

        elif self.mode in self.anomaly_list and elapsed >= self.anomaly_duration:
            print(f"\n*** FIN anomalie ({self.mode}), début RECOVERY ***\n")
            self.recovery_targets = self.get_diurnal_targets()
            self.mode = "recovery"
            self.mode_start = now

        elif self.mode == "recovery" and elapsed >= self.recovery_duration:
            print(f"\n*** FIN recovery, retour au normal ***\n")
            self.mode = "normal"
            self.mode_start = now
            self.recovery_targets = None

    def update_values(self):
        self.apply_drift()
        self.check_irrigation()

        target_temp, target_hum, target_soil = self.get_diurnal_targets()

        if self.mode == "normal" or self.mode == "recovery":
            if self.mode == "recovery" and self.recovery_targets is not None:
                progress = (self.current_time - self.mode_start).total_seconds() / self.recovery_duration
                progress = min(max(progress, 0.0), 1.0)
                target_temp = self.current_temperature + (self.recovery_targets[0] - self.current_temperature) * progress
                target_hum = self.current_humidity + (self.recovery_targets[1] - self.current_humidity) * progress
                target_soil = self.current_soil_moisture + (self.recovery_targets[2] - self.current_soil_moisture) * progress

            
            self.current_temperature += 0.15 * (target_temp - self.current_temperature) + random.uniform(-0.3, 0.3) + self.drift_temp
            self.current_humidity += 0.15 * (target_hum - self.current_humidity) + random.uniform(-0.8, 0.8) + self.drift_hum
            self.current_soil_moisture += 0.1 * (target_soil - self.current_soil_moisture) + random.uniform(-0.15, 0.15) + self.drift_soil

        else:
            # Anomaly handling
            progress = min(1.0, (self.current_time - self.mode_start).total_seconds() / 10)

            if self.mode == "temp_spike":
                anomaly_target_temp = 38.0
                self.current_temperature += progress * (anomaly_target_temp - self.current_temperature) / 5
                if self.cross_effects:
                    self.current_humidity -= progress * 3 / 5

            elif self.mode == "temp_low":
                anomaly_target_temp = 8.0
                self.current_temperature += progress * (anomaly_target_temp - self.current_temperature) / 5
                if self.cross_effects:
                    self.current_humidity += progress * 2 / 5

            elif self.mode == "humidity_spike":
                anomaly_target_hum = 95.0
                self.current_humidity += progress * (anomaly_target_hum - self.current_humidity) / 5
                if self.cross_effects:
                    self.current_temperature -= progress * 1 / 5

            elif self.mode == "humidity_drop":
                anomaly_target_hum = 20.0
                self.current_humidity += progress * (anomaly_target_hum - self.current_humidity) / 5
                if self.cross_effects:
                    self.current_soil_moisture -= progress * 2 / 5

            elif self.mode == "moisture_drop":
                # Chute rapide >10% en 1-3h
                self.current_soil_moisture -= progress * 35 / 3
                if self.cross_effects:
                    self.current_humidity -= progress * 4 / 3

            elif self.mode == "moisture_leak":
                anomaly_target_soil = 85.0
                self.current_soil_moisture += progress * (anomaly_target_soil - self.current_soil_moisture) / 5
                if self.cross_effects:
                    self.current_humidity += progress * 3 / 5

        # Limites physiques
        self.current_temperature = max(5, min(45, self.current_temperature))
        self.current_humidity = max(15, min(95, self.current_humidity))
        self.current_soil_moisture = max(25, min(85, self.current_soil_moisture))

    def generate_reading(self):
        self.switch_mode_if_needed()
        self.update_values()

        return {
            "timestamp": self.current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "mode": self.mode,
            "temperature": round(self.current_temperature, 2),
            "humidity": round(self.current_humidity, 2),
            "soil_moisture": round(self.current_soil_moisture, 2),
        }

    def display(self, r):
        if r['mode'] == 'normal':
            mode_display = f"\033[92m{r['mode']}\033[0m"
        elif r['mode'] == 'recovery':
            mode_display = f"\033[93m{r['mode']}\033[0m"
        else:
            mode_display = f"\033[91m{r['mode']}\033[0m"

        print(f"[{r['timestamp']}] Mode = {mode_display}")

        temp_str = f"{r['temperature']} °C"
        if r['temperature'] > 32 or r['temperature'] < 10:
            temp_str = f"\033[91m{temp_str} !\033[0m"

        hum_str = f"{r['humidity']} %"
        if r['humidity'] > 85 or r['humidity'] < 30:
            hum_str = f"\033[91m{hum_str} !\033[0m"

        soil_str = f"{r['soil_moisture']} %"
        if r['soil_moisture'] > 75 or r['soil_moisture'] < 35:
            soil_str = f"\033[91m{soil_str} !\033[0m"

        print(f"   Température :      {temp_str}")
        print(f"   Humidité air :     {hum_str}")
        print(f"   Humidité du sol :  {soil_str}")
        print("-" * 60)

    def run(self, minutes=None, interval=2):
        print("\n=== SIMULATION CAPTEURS INTELLIGENTS ===\n")
        print("Légende: \033[92mnormal\033[0m | \033[93mrecovery\033[0m | \033[91manomalie\033[0m | \033[91m!\033[0m = hors plage")
        print(f"Cross-effects: {'ON' if self.cross_effects else 'OFF'}")
        print(f"Intervalle de lecture: {interval}s (changez à 300s pour 5min en production)")
        print("=" * 60)

        if minutes is not None:
            end_time = self.current_time + timedelta(minutes=minutes)
            running_condition = lambda: self.current_time < end_time
        else:
            running_condition = lambda: True

        while running_condition():
            try:
                r = self.generate_reading()
                self.display(r)

                self.timestamps.append(self.current_time)
                self.temps.append(r["temperature"])
                self.humids.append(r["humidity"])
                self.moistures.append(r["soil_moisture"])

                self.advance_time(interval)

            except KeyboardInterrupt:
                print("\n\n*** SIMULATION INTERROMPUE PAR L'UTILISATEUR ***\n")
                break


if __name__ == "__main__":
    # Pour tester rapidement avec intervalle de 2s
    start_anomaly = datetime.now() + timedelta(minutes=2)
    anomalies = [
        "temp_spike",
        "temp_low",
        "humidity_spike",
        "humidity_drop",
        "moisture_drop",
        "moisture_leak"
    ]
    random_anomaly = random.choice(anomalies)
    
    scenario = [(start_anomaly, random_anomaly, 60)]  # 60s d'anomalie pour test

    print("\n*** ANOMALIE ALÉATOIRE DU SCÉNARIO :", random_anomaly, "***\n")

    sim = CleanSensorSimulator(
        plot_id=1,
        scenario=scenario,
        fast_simulate=False,
        sim_speed_factor=1,
        cross_effects=False,
    )
    
    # Pour test: interval=2s, pour production: interval=300 (5 minutes)
    sim.run(minutes=10, interval=2)