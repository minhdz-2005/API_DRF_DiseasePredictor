from django.shortcuts import render
from rest_framework import viewsets
from .models import Statistics, Treatments
from .serializers import StatisticsSerializer, TreatmentsSerializer

class StatisticsViewSet(viewsets.ModelViewSet):
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer

class TreatmentsViewSet(viewsets.ModelViewSet):
    queryset = Treatments.objects.all()
    serializer_class = TreatmentsSerializer