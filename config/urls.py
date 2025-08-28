"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from api.views import (
    SymptomListView,
    DiseaseListView,
    StatisticListView,
    TreatmentListView,
    PredictDiseaseView
    )

def home(request):
    html_content = """
    <h1>Welcome to Disease Predictor API!</h1>
    <ul>
        <li><a href="/api/">API Root</a></li>
        <li><a href="/api/docs/">API Documentation (Swagger)</a></li>
        <li><a href="/api/docs/redoc/">API Documentation (ReDoc)</a></li>
    </ul>
    """
    return HttpResponse(html_content)

urlpatterns = [
    path('', home),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path("symptoms/", SymptomListView.as_view(), name="symptom-list"),
    path("diseases/", DiseaseListView.as_view(), name="disease-list"),
    path("statistics/", StatisticListView.as_view(), name="statistics-list"),
    path("treatments/", TreatmentListView.as_view(), name="treatments-list"),
    path("predict/", PredictDiseaseView.as_view(), name="predict-disease"),

]
