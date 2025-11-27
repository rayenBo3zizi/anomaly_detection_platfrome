from django.db import models

class CropType(models.TextChoices):
    CEREALS = 'cereals', 'Cereals'
    VEGETABLES = 'vegetables', 'Vegetables'
    FRUITS = 'fruits', 'Fruits'


class CropVariety(models.TextChoices):
    # Cereals
    DURUM_WHEAT = 'durum_wheat', 'Durum Wheat'
    SOFT_WHEAT = 'soft_wheat', 'Soft Wheat'
    HYBRID_CORN = 'hybrid_corn', 'Hybrid Corn'
    SWEET_CORN = 'sweet_corn', 'Sweet Corn'
    BASMATI_RICE = 'basmati_rice', 'Basmati Rice'
    WINTER_BARLEY = 'winter_barley', 'Winter Barley'
    OATS = 'oats', 'Oats'
    
    # Vegetables
    CHERRY_TOMATO = 'cherry_tomato', 'Cherry Tomato'
    ROUND_TOMATO = 'round_tomato', 'Round Tomato'
    NANTES_CARROT = 'nantes_carrot', 'Nantes Carrot'
    ROMAINE_LETTUCE = 'romaine_lettuce', 'Romaine Lettuce'
    OAKLEAF_LETTUCE = 'oakleaf_lettuce', 'Oakleaf Lettuce'
    DIAMOND_ZUCCHINI = 'diamond_zucchini', 'Diamond Zucchini'
    BLACK_PEARL_EGGPLANT = 'black_pearl_eggplant', 'Black Pearl Eggplant'
    RED_BELL_PEPPER = 'red_bell_pepper', 'Red Bell Pepper'
    CUCUMBER = 'cucumber', 'Cucumber'
    
    # Fruits
    VALENCIA_ORANGE = 'valencia_orange', 'Valencia Orange'
    GOLDEN_APPLE = 'golden_apple', 'Golden Apple'
    GRANNY_SMITH_APPLE = 'granny_smith_apple', 'Granny Smith Apple'
    CHARDONNAY_GRAPE = 'chardonnay_grape', 'Chardonnay Grape'
    CABERNET_GRAPE = 'cabernet_grape', 'Cabernet Grape'
    CAVENDISH_BANANA = 'cavendish_banana', 'Cavendish Banana'
    LIME = 'lime', 'Lime'
    MANDARIN = 'mandarin', 'Mandarin'
    APRICOT = 'apricot', 'Apricot'
    PEACH = 'peach', 'Peach'

class SensorType(models.TextChoices):
    MOISTURE = 'moisture', 'Soil Moisture'
    TEMPERATURE = 'temperature', 'Air Temperature'
    HUMIDITY = 'humidity', 'Air Humidity'


class AnomalyType(models.TextChoices):
    MOISTURE_DROP = 'moisture_drop', 'Moisture Drop'
    MOISTURE_SPIKE = 'moisture_spike', 'Moisture Spike'
    TEMPERATURE_HIGH = 'temperature_high', 'High Temperature'
    TEMPERATURE_LOW = 'temperature_low', 'Low Temperature'
    HUMIDITY_HIGH = 'humidity_high', 'High Humidity'
    HUMIDITY_LOW = 'humidity_low', 'Low Humidity'
    SENSOR_DRIFT = 'sensor_drift', 'Sensor Drift'
    SENSOR_FAILURE = 'sensor_failure', 'Sensor Failure'
    DATA_GAP = 'data_gap', 'Missing Data'

class SeverityLevel(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'

