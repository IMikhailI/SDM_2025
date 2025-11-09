from rest_framework import serializers
from .models import Course, Lesson, UserProgress, GeneratedTask

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


# Дополнительное задание

class GeneratedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedTask
        fields = ['id', 'lesson', 'user', 'task_text', 'solution', 'student_answer', 'is_correct', 'created_at']
        read_only_fields = ['id', 'user', 'created_at', 'solution', 'student_answer', 'is_correct']

class CheckTaskRequestSerializer(serializers.Serializer):
    answer = serializers.CharField()

class CheckTaskResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    is_correct = serializers.BooleanField()