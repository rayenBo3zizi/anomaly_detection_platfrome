import threading
import time
from datetime import datetime, timedelta
import os
import random

from decouple import Config, RepositoryEnv
from genClaude import CleanSensorSimulator
from HttpGenerator import HTTPEnabledSensorSimulator  


def run_simulation_for_plot(plot_id, http_sim, seed_offset=0, interval=300):
    """
    Thread : simulation pour un seul plot.
    Mode production : envoi toutes les 5 minutes (300s)
    
    Args:
        plot_id: ID du plot
        http_sim: Instance HTTP pour envoi (None = affichage seulement)
        seed_offset: Décalage pour la seed (crée de la variabilité)
        interval: Intervalle entre lectures en secondes (300 = 5min)
    """
    
    # Scénario : anomalie dans 30-90 minutes (adapté pour intervalle 5min)
    start_anomaly = datetime.now() + timedelta(minutes=random.uniform(30, 90))
    anomalies = [
        "temp_spike",
        "temp_low",
        "humidity_spike",
        "humidity_drop",
        "moisture_drop",
        "moisture_leak"
    ]
    random_anomaly = random.choice(anomalies)
    scenario = [(start_anomaly, random_anomaly, 3600)]  # 1h d'anomalie
    
    print(f"\n🌱 Plot {plot_id} : Anomalie '{random_anomaly}' prévue vers {start_anomaly.strftime('%H:%M:%S')}\n")
    
    # Créer le simulateur avec durées ajustées pour intervalle 5min
    sim = CleanSensorSimulator(
        plot_id=plot_id,
        scenario=scenario,
        fast_simulate=False,
        sim_speed_factor=1,
        cross_effects=False,
        seed=(plot_id * 42 + seed_offset) if seed_offset else None
    )
    
    # AJUSTEMENT DES DURÉES pour intervalle 5min (12 lectures/heure)
    # Mode normal : 2-3 heures (24-36 lectures)
    sim.normal_duration = random.uniform(2 * 3600, 3 * 3600)
    # Anomalie : 1-2 heures (12-24 lectures)
    sim.anomaly_duration = random.uniform(1 * 3600, 2 * 3600)
    # Recovery : 30-45 minutes (6-9 lectures)
    sim.recovery_duration = random.uniform(30 * 60, 45 * 60)
    
    iteration = 0
    
    print(f"⚙️  Plot {plot_id} configuré : Normal={sim.normal_duration/3600:.1f}h, "
          f"Anomalie={sim.anomaly_duration/3600:.1f}h, Recovery={sim.recovery_duration/60:.0f}min")
    
    while True:
        try:
            # Générer lecture
            r = sim.generate_reading()
            
            iteration += 1
            
            # Affichage console (toutes les 3 lectures = 15min)
            if iteration % 3 == 0:
                print(f"\n📌 PLOT {plot_id} [{r['timestamp']}] (lecture #{iteration})")
                sim.display(r)
            
            # Envoyer à Django si disponible
            if http_sim is not None:
                try:
                    http_sim.send_reading(plot_id, "temperature", r["temperature"])
                    http_sim.send_reading(plot_id, "humidity", r["humidity"])
                    http_sim.send_reading(plot_id, "moisture", r["soil_moisture"])
                    
                    if iteration % 3 == 0:
                        print(f"✅ Plot {plot_id} : Données envoyées à Django")
                        
                except Exception as e:
                    if iteration % 6 == 0:  # Log erreur toutes les 30min
                        print(f"⚠️  Erreur envoi HTTP plot {plot_id}: {e}")
            
            # Stocker pour plotting (optionnel)
            sim.timestamps.append(sim.current_time)
            sim.temps.append(r["temperature"])
            sim.humids.append(r["humidity"])
            sim.moistures.append(r["soil_moisture"])
            
            # Avancer le temps
            sim.advance_time(interval)
            
        except KeyboardInterrupt:
            print(f"\n🛑 Plot {plot_id} : Arrêt demandé")
            break
        except Exception as e:
            print(f"❌ Erreur dans thread plot {plot_id}: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(60)  # Attendre 1min avant de réessayer


def test_single_plot_fast():
    """Test rapide : 1 plot avec intervalle 2s (pour debug)"""
    print("\n🧪 TEST RAPIDE: Simulation 1 plot (intervalle 2s)\n")
    
    start_anomaly = datetime.now() + timedelta(minutes=2)
    random_anomaly = random.choice([
        "temp_spike", "temp_low", "humidity_spike",
        "humidity_drop", "moisture_drop", "moisture_leak"
    ])
    scenario = [(start_anomaly, random_anomaly, 120)]  # 2min d'anomalie
    
    print(f"*** ANOMALIE : {random_anomaly} dans 2 minutes ***\n")
    
    sim = CleanSensorSimulator(
        plot_id=1,
        scenario=scenario,
        fast_simulate=False,
        sim_speed_factor=1,
        cross_effects=False,
    )
    
    # Durées courtes pour test rapide
    sim.normal_duration = 5 * 60  # 5min
    sim.anomaly_duration = 2 * 60  # 2min
    sim.recovery_duration = 2 * 60  # 2min
    
    sim.run(minutes=15, interval=2)


def test_multi_plots_display_only():
    """Test : Tous les plots de la BD - AFFICHAGE SEULEMENT (intervalle 2s)"""
    print("\n🧪 TEST: Simulation multi-plots - MODE AFFICHAGE RAPIDE\n")
    print("=" * 60)
    
    # Récupérer les plots depuis la BD
    plots = []
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        env_path = os.path.join(project_dir, "Anomaly_Detection_Platform", ".env")
        config = Config(RepositoryEnv(env_path))
        
        BASE_URL = "http://localhost:8000"
        USERNAME = config("ADMIN_NAME")
        PASSWORD = config("ADMIN_PASSWORD")
        
        token = HTTPEnabledSensorSimulator.get_jwt_token(USERNAME, PASSWORD)
        http_sim = HTTPEnabledSensorSimulator(BASE_URL, token=token)
        plots = http_sim.fetch_plots()
        
        print(f"✅ Connecté à Django : {len(plots)} plots récupérés depuis la BD")
        
    except Exception as e:
        print(f"⚠️  Erreur connexion Django: {e}")
        print("⚠️  Utilisation de 3 plots de test par défaut")
        plots = [{"id": 1}, {"id": 2}, {"id": 3}]
    
    if not plots:
        print("❌ Aucun plot disponible")
        return
    
    print(f"\n🚀 Lancement de {len(plots)} simulateurs (intervalle 2s pour test)...\n")
    
    threads = []
    for idx, plot in enumerate(plots):
        plot_id = plot["id"]
        
        thread = threading.Thread(
            target=run_simulation_for_plot,
            args=(plot_id, None, idx * 100, 2),  # interval=2s pour test rapide
            daemon=True,
            name=f"Plot-{plot_id}"
        )
        thread.start()
        threads.append(thread)
        time.sleep(0.5)
    
    print(f"\n🟢 {len(threads)} simulateurs actifs (affichage uniquement)")
    print("💡 Ctrl+C pour arrêter\n")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt...")


def run_production():
    """MODE PRODUCTION : Envoi toutes les 5 minutes (300s)"""
    print("\n🚀 MODE PRODUCTION : Simulation avec envoi BD toutes les 5 minutes\n")
    print("=" * 60)
    
    # Charger environnement
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    env_path = os.path.join(project_dir, "Anomaly_Detection_Platform", ".env")
    
    http_sim = None
    plots = []
    
    try:
        config = Config(RepositoryEnv(env_path))
        BASE_URL = "http://localhost:8000"
        USERNAME = config("ADMIN_NAME")
        PASSWORD = config("ADMIN_PASSWORD")
        
        # Authentification
        token = HTTPEnabledSensorSimulator.get_jwt_token(USERNAME, PASSWORD)
        http_sim = HTTPEnabledSensorSimulator(BASE_URL, token=token)
        
        # Charger plots depuis Django
        plots = http_sim.fetch_plots()
        print(f"✅ Connecté à Django : {len(plots)} plots trouvés")
        
    except Exception as e:
        print(f"❌ ERREUR Django: {e}")
        print("❌ MODE PRODUCTION nécessite une connexion Django valide")
        return
    
    if not plots:
        print("❌ Aucun plot disponible dans la BD")
        return

    print(f"\n🚀 Démarrage de {len(plots)} simulateurs (intervalle 5min = 300s)...\n")
    print("⏰ Prochaine lecture dans 5 minutes...")
    print("📊 Affichage console toutes les 15 minutes (3 lectures)")
    print("=" * 60)
    
    # Démarrer 1 thread par plot avec intervalle 5min
    threads = []
    for idx, plot in enumerate(plots):
        plot_id = plot["id"]
        
        thread = threading.Thread(
            target=run_simulation_for_plot,
            args=(plot_id, http_sim, idx * 123, 300),  # interval=300s (5min)
            daemon=True,
            name=f"Plot-{plot_id}"
        )
        thread.start()
        threads.append(thread)
        time.sleep(1)  # Décalage de 1s entre threads

    print(f"\n🟢 {len(threads)} simulateurs en cours (production)")
    print("💡 Appuyez sur Ctrl+C pour arrêter\n")
    print("=" * 60)

    try:
        while True:
            time.sleep(30)  # Check toutes les 30s
            
            # Vérifier threads actifs
            alive = sum(1 for t in threads if t.is_alive())
            if alive < len(threads):
                print(f"⚠️  ALERTE : {len(threads) - alive} thread(s) terminé(s) !")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé par l'utilisateur")
        print("⏳ Les threads vont se terminer...")
        time.sleep(2)


if __name__ == "__main__":
    
    # ==========================================
    # DÉCOMMENTEZ L'OPTION QUE VOUS VOULEZ :
    # ==========================================
    
    # OPTION 1: Test rapide 1 plot (intervalle 2s pour debug)
    # test_single_plot_fast()
    # exit()
    
    # OPTION 2: Test multi-plots affichage rapide (intervalle 2s)
    # test_multi_plots_display_only()
    # exit()
    
    # OPTION 3: PRODUCTION - Envoi à Django toutes les 5min (300s)
    run_production()