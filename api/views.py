from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import csv
import os
import joblib

from .models import Statistics, Treatments
from .serializers import StatisticsSerializer, TreatmentsSerializer
from .predict_utils import predict_top_k   # import hàm dự đoán


# Update statistics function for new disease
def update_statistics(disease_name: str):
    stat, created = Statistics.objects.get_or_create(disease=disease_name)
    stat.count += 1
    stat.save()


# Đường dẫn file dữ liệu
SYMPTOM_FILE = os.path.join(os.path.dirname(__file__), 'data', 'symptoms.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_model', 'rf_model.pkl')
ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'ml_model', 'label_encoder.pkl')

# Load model + encoder
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)


# ==== API Views ====

class SymptomListView(APIView):
    def get(self, request):
        with open(SYMPTOM_FILE, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            symptoms = [row["symptom"] for row in reader]
        return Response(symptoms)
    

class DiseaseListView(APIView):
    def get(self, request):
        diseases = label_encoder.classes_.tolist()
        return Response({"diseases": diseases})


class StatisticListView(APIView):
    def get(self, request):
        stats = Statistics.objects.all()
        serializer = StatisticsSerializer(stats, many=True)
        return Response({"statistics": serializer.data})


class TreatmentListView(APIView):
    def get(self, request):
        treatments = Treatments.objects.all()
        serializer = TreatmentsSerializer(treatments, many=True)
        return Response({"treatments": serializer.data})


# ==== Predict Disease API ====
class PredictDiseaseView(APIView):
    def post(self, request):
        # Input: danh sách triệu chứng
        symptoms = request.data.get("symptoms", [])

        # Đọc toàn bộ triệu chứng chuẩn từ file CSV
        with open(SYMPTOM_FILE, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            all_symptoms = [row["symptom"] for row in reader]

        # B1: Vector hóa input
        input_vector = [1 if s in symptoms else 0 for s in all_symptoms]

        # Kiểm tra hợp lệ
        if sum(input_vector) == 0:
            return Response(
                {"detail": "Không có triệu chứng hợp lệ được gửi lên."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # B2: Dự đoán top-k
        results = predict_top_k(model, label_encoder, input_vector, k=3)

        # B3: Lưu thống kê (lấy bệnh có xác suất cao nhất)
        top_disease = results[0][0]
        update_statistics(top_disease)

        # B4: Trả về kết quả
        return Response({
            "predictions": [
                {"disease": disease, "probability": f"{round(prob * 100, 2)}%"}
                for disease, prob in results
            ]
        })
