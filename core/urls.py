from rest_framework.routers import DefaultRouter
from .views import FarmProfileViewSet, FieldPlotViewSet, SensorReadingViewSet, AnomalyEventViewSet, AgentRecommendationViewSet


router = DefaultRouter()
router.register(r'farmprofiles', FarmProfileViewSet)
router.register(r'fieldplots', FieldPlotViewSet, basename='fieldplots')

router.register(r'sensor-readings', SensorReadingViewSet)
router.register(r'anomalies', AnomalyEventViewSet)
router.register(r'recommendations', AgentRecommendationViewSet)


urlpatterns = router.urls
