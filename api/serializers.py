from rest_framework import serializers
from .models import Statistics, Treatments

class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = '__all__'

class TreatmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatments
        fields = '__all__'