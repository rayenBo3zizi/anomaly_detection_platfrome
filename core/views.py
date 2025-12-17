from rest_framework import viewsets
from .models import FarmProfile, FieldPlot, SensorReading, AnomalyEvent, AgentRecommendation, UserProfile
from .serializers import FarmProfileSerializer, FieldPlotSerializer, SensorReadingSerializer, AnomalyEventSerializer, AgentRecommendationSerializer
from .permissions import IsOwnerOrAdmin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

class FarmProfileViewSet(viewsets.ModelViewSet):
    queryset = FarmProfile.objects.all()
    serializer_class = FarmProfileSerializer
    permission_classes = [IsOwnerOrAdmin]


class FieldPlotViewSet(viewsets.ModelViewSet):
    serializer_class = FieldPlotSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user

        
        try:
            profile = user.userprofile  
            if profile.role == 'admin':
                return FieldPlot.objects.all()
        except (AttributeError, UserProfile.DoesNotExist):
            pass

       
        if user.farmprofile_set.exists():
            return FieldPlot.objects.filter(farm__owner=user)

        
        return FieldPlot.objects.none()


class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    @action(detail=False, methods=['get'], url_path='plot/(?P<plot_id>[^/.]+)')
    def by_plot(self, request, plot_id=None):
        """GET /api/sensor-readings/plot/<plot_id>/"""
        today = timezone.localdate() 
        readings = SensorReading.objects.filter(plot_id=plot_id, timestamp__date=today).order_by('timestamp')
        serializer = self.get_serializer(readings, many=True)
        return Response(serializer.data)

class AnomalyEventViewSet(viewsets.ModelViewSet):
    queryset = AnomalyEvent.objects.all()
    serializer_class = AnomalyEventSerializer


class AgentRecommendationViewSet(viewsets.ModelViewSet):
    queryset = AgentRecommendation.objects.all()
    serializer_class = AgentRecommendationSerializer









