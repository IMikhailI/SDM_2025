from rest_framework import serializers
from .models import Course, Lesson, UserProgress

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description']

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'content']

class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = ['id', 'user', 'lesson', 'completed_at']
        read_only_fields = ['user', 'completed_at']

class AskRequestSerializer(serializers.Serializer):
    question = serializers.CharField()
    provider = serializers.ChoiceField(choices=["gigachat", "google"], required=False)

class AskResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    provider = serializers.CharField()