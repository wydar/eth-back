from rest_framework import serializers

from eth.models import Station, Measures


class StationSerializer(serializers.ModelSerializer):
    """
    Station serializer
    """
    class Meta:
        model = Station
        fields = '__all__'


class MeasureSerializer(serializers.ModelSerializer):
    """
    Measures serializer
    """
    class Meta:
        model = Measures
        fields = '__all__'
