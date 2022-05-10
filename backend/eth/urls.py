from rest_framework import routers

from eth.views import StationViewSet

router = routers.SimpleRouter()
# router.register(r'measures', MeasuresViewSet)
router.register(r'stations', StationViewSet)

urlpatterns = []


urlpatterns = router.urls
