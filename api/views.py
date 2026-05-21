from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

import csv
import os
import joblib

from .models import Statistics, Treatments, User, Blog, Comment, PredictionHistory
from .serializers import StatisticsSerializer, TreatmentsSerializer, BlogSerializer, CommentSerializer, UserSerializer, PredictionHistorySerializer
from .predict_utils import predict_top_k   # import hàm dự đoán


# Update statistics function for new disease
def update_statistics(disease_name: str):
    stat, created = Statistics.objects.get_or_create(disease=disease_name)
    if stat.count is None:
        stat.count = 0
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
@extend_schema(
    description="API dự đoán bệnh dựa trên danh sách triệu chứng",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'symptoms': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Danh sách các triệu chứng'
                }
            }
        }
    },
    responses={
        200: {
            'description': 'Successful prediction',
            'type': 'object',
            'properties': {
                'predictions': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'disease': {'type': 'string'},
                            'probability': {'type': 'string'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - No valid symptoms provided'
        }
    },
    examples=[
        OpenApiExample(
            'Example Request',
            value={'symptoms': ["itching",  "skin_rash",  "nodal_skin_eruptions"]},
            request_only=True
        ),
        OpenApiExample(
            'Example Response',
            value={
                'predictions': [
                    {
                        "disease": "Fungal infection",
                        "probability": "100.0%"
                    },
                    {
                        "disease": "Varicose veins",
                        "probability": "0.0%"
                    },
                    {
                        "disease": "Urinary tract infection",
                        "probability": "0.0%"
                    }
                ]
            },
            response_only=True
        )
    ]
)
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









# ==== User Registration API ====
class RegisterView(APIView):
    """
    API đăng ký tài khoản người dùng mới
    """
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role", "user")  # mặc định là user

        # Kiểm tra đầu vào
        if not username or not email or not password:
            return Response({"detail": "Thiếu thông tin đăng ký."}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra trùng tên hoặc email
        if User.objects.filter(username=username).exists():
            return Response({"detail": "Tên người dùng đã tồn tại."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"detail": "Email đã được sử dụng."}, status=status.HTTP_400_BAD_REQUEST)

        # Mã hóa mật khẩu
        hashed_password = make_password(password)

        # Tạo user
        user = User.objects.create(
            username=username,
            email=email,
            password=hashed_password,
            role=role
        )

        return Response({
            "message": "Đăng ký thành công!",
            "user": {
                "id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)


# ==== User Login API ====
class LoginView(APIView):
    """
    API đăng nhập (xác thực username + password)
    """
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"detail": "Thiếu tên đăng nhập hoặc mật khẩu."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "Tên đăng nhập không tồn tại."}, status=status.HTTP_404_NOT_FOUND)

        # Kiểm tra mật khẩu
        if not check_password(password, user.password):
            return Response({"detail": "Sai mật khẩu."}, status=status.HTTP_401_UNAUTHORIZED)

        # Nếu đúng → trả thông tin user
        return Response({
            "message": "Đăng nhập thành công!",
            "user": {
                "id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_200_OK)
    

class BlogViewSet(viewsets.ModelViewSet):
    """
    CRUD API cho Blog
    - User: tạo, xem, sửa, xóa bài viết của mình.
    - Admin: duyệt và quản lý tất cả bài viết.
    """
    queryset = Blog.objects.all().order_by('-created_at')
    serializer_class = BlogSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        blog_id = self.request.query_params.get('blog')
        author_id = self.request.query_params.get('author')

        # Nếu có query ?blog= thì lọc comment theo blog đó
        if blog_id:
            queryset = queryset.filter(blog_id=blog_id)

        if author_id:
            queryset = queryset.filter(author_id=author_id)

        return queryset


class PredictionHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = PredictionHistorySerializer

    def get_queryset(self):
        queryset = PredictionHistory.objects.all()
        user_id = self.request.query_params.get("user", None)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        return queryset

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('created_at')
    serializer_class = UserSerializer