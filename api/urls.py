from rest_framework.routers import DefaultRouter
from .views import StatisticsViewSet, TreatmentsViewSet

router = DefaultRouter()
router.register(r'statistics', StatisticsViewSet)
router.register(r'treatments', TreatmentsViewSet)

urlpatterns = router.urls
