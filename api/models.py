# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Statistics(models.Model):
    disease = models.CharField(max_length=100, unique=True)
    count = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'statistics'


class Treatments(models.Model):
    field_id = models.CharField(db_column='mongo_id', primary_key=True, max_length=24)  # Field renamed because it started with '_'.
    disease = models.CharField(max_length=100)
    infomation = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'treatments'

# =========================
# CUSTOM TABLES FOR UPDATE
# =========================

class User(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'user'

    def __str__(self):
        return f"{self.username} ({self.role})"


class Blog(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    blog_id = models.AutoField(primary_key=True)
    author = models.ForeignKey('User', on_delete=models.CASCADE, db_column='author_id', related_name='blogs')
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'blog'

    def __str__(self):
        return f"{self.title} - {self.status}"


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, db_column='blog_id', related_name='comments')
    author = models.ForeignKey('User', on_delete=models.CASCADE, db_column='author_id', related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'comment'

    def __str__(self):
        return f"Comment by {self.author.username} on {self.blog.title}"

class PredictionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    symptoms = models.JSONField()  # Lưu danh sách triệu chứng dạng mảng JSON
    disease_1 = models.CharField(max_length=100)
    disease_2 = models.CharField(max_length=100)
    disease_3 = models.CharField(max_length=100)
    prob_1 = models.FloatField()
    prob_2 = models.FloatField()
    prob_3 = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prediction_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"