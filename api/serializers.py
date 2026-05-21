from rest_framework import serializers
from .models import Statistics, Treatments, User, Blog, Comment, PredictionHistory

from django.contrib.auth.hashers import make_password

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

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Blog


# ==== USER SERIALIZER ====
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'password', 'role', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}  # không trả mật khẩu ra khi GET
        }

    def create(self, validated_data):
        # Mã hóa mật khẩu khi tạo user
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


# ==== BLOG SERIALIZER ====
class BlogSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)  # ✅ Trả về đầy đủ thông tin author
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='author', write_only=True
    )  # ✅ Cho phép gửi author_id khi POST blog mới

    class Meta:
        model = Blog
        fields = ['blog_id', 'author', 'author_id', 'title', 'content', 'status', 'created_at']



# ==== COMMENT SERIALIZER ====
class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    blog = BlogSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='author', write_only=True
    )
    blog_id = serializers.PrimaryKeyRelatedField(
        queryset=Blog.objects.all(), source='blog', write_only=True
    )

    class Meta:
        model = Comment
        fields = ['comment_id', 'author', 'author_id', 'blog', 'blog_id', 'content', 'created_at']


class PredictionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionHistory
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'