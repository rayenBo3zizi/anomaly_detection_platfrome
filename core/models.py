from django.db import models
from .enumerations import *
from django.contrib.auth.models import User

class FarmProfile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=300)
    size = models.FloatField(help_text="Size in hectares")
    crop_type = models.CharField(
        max_length=50,
        choices=CropType.choices,
        default=CropType.VEGETABLES
    )


    class Meta:
        verbose_name = "Farm Profile"
        verbose_name_plural = "Farm Profiles"
        db_table = 'farm_profiles'
        constraints = [
            models.UniqueConstraint(fields=['owner', 'location'], name='unique_farm_per_owner_location')
        ]


class FieldPlot(models.Model):
    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE)
    crop_variety = models.CharField(
        max_length=50,
        choices=CropVariety.choices,
        default=CropVariety.CHERRY_TOMATO
    )

    class Meta:
        verbose_name = "Field Plot"
        verbose_name_plural = "Field Plots"
        db_table = 'field_plots'
        ordering = ['farm']
        constraints = [
            models.UniqueConstraint(fields=['farm', 'crop_variety'], name='unique_plot_per_farm_crop')
        ]


class SensorReading(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE)
    sensor_type = models.CharField(
        max_length=20,
        choices=SensorType.choices
    )
    value = models.FloatField()
    source = models.CharField(max_length=50, default='simulator')
    class Meta:
        verbose_name = "Sensor Reading"
        verbose_name_plural = "Sensor Readings"
        db_table = 'sensor_readings'
        ordering = ['-timestamp']
        

class AnomalyEvent(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE)
    anomaly_type = models.CharField(
        max_length=20,
        choices=AnomalyType.choices
    )
    severity = models.CharField(
        max_length=10,
        choices=SeverityLevel.choices,
        default=SeverityLevel.MEDIUM
    )
    model_confidence = models.FloatField(help_text="Model confidence (0-1)")
    sensor_reading = models.ForeignKey(SensorReading, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Anomaly Event"
        verbose_name_plural = "Anomaly Events"
        db_table = 'anomaly_events'
        ordering = ['-timestamp']
        constraints = [
            models.UniqueConstraint(fields=['timestamp', 'plot', 'anomaly_type'], name='unique_anomaly_per_plot_time_type')
        ]


class AgentRecommendation(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    anomaly_event = models.ForeignKey(AnomalyEvent, on_delete=models.CASCADE)
    recommended_action = models.CharField(
        max_length=50
        
    )
    explanation_text = models.TextField()
    confidence = models.CharField(
        max_length=20
    )


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('farmer', 'Farmer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')



from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def whoami(request):
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "authenticated": request.user.is_authenticated
    })
