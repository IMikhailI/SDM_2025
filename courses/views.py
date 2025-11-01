from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
import requests, os
import re

from .models import Course, Lesson, UserProgress
from .serializers import CourseSerializer, LessonSerializer, UserProgressSerializer

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user and request.user.is_authenticated

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('course').all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_lesson(request, pk: int):
    lesson = get_object_or_404(Lesson, pk=pk)
    try:
        progress = UserProgress.objects.create(user=request.user, lesson=lesson)
    except IntegrityError:
        progress = UserProgress.objects.get(user=request.user, lesson=lesson)
    return Response(UserProgressSerializer(progress).data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ask_lesson(request, pk: int):
    lesson = get_object_or_404(Lesson, pk=pk)
    question = (request.data.get("question") or "").strip()
    context = (lesson.content or "").strip()

    # Ограничим размер контекста на всякий случай
    context = context[:8000]

    # Строгая инструкция: отвечать только из контекста
    system_text = (
        "Ты — AI-репетитор. Дай развернутый, но четкий ответ, "
        "основанный только на предоставленном контексте. "
        "Если ответа в контексте нет, так и скажи: 'Ответ не найден в контексте.'"
    )
    user_text = (
        f"Контекст урока:\n{context}\n\n"
        f"Вопрос студента:\n{question}"
    )

    api_key = os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
    print("GOOGLE_API_KEY_LOADED:", bool(api_key))
    fallback = "Ответ не найден в контексте."

    if not api_key:
        return Response({"answer": fallback})

    try:
        # REST-вызов Gemini (v1beta)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload = {
            "system_instruction": {"parts": [{"text": system_text}]},
            "contents": [
                {"role": "user", "parts": [{"text": user_text}]}
            ],
            "generation_config": {
                "temperature": 0.2,
                "maxOutputTokens": 256
            }
        }
        # Ключ передаем как query-параметр
        resp = requests.post(url, params={"key": api_key}, json=payload, timeout=20)
        data = resp.json()

        # Извлечь первый текстовый ответ
        answer = fallback
        for cand in (data.get("candidates") or []):
            parts = ((cand.get("content") or {}).get("parts") or [])
            if parts and parts[0].get("text"):
                answer = parts[0]["text"].strip()
                break

        # На всякий случай, если модель «забылась»
        if not answer:
            answer = fallback

        return Response({"answer": answer})
    except Exception:
        return Response({"answer": fallback})
