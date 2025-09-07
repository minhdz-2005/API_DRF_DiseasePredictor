from rest_framework import serializers
from .models import Statistics, Treatments

class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = '__all__'

class TreatmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatments
        exclude = ('field_id',)

class PredictRequestSerializer(serializers.Serializer):
    symptoms = serializers.ListField(
        child=serializers.CharField(),
        help_text="Danh sách các triệu chứng để dự đoán bệnh"
    )