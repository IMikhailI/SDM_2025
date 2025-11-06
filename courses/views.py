from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, OpenApiParameter 
from drf_spectacular.types import OpenApiTypes
import requests, os
import re

from .models import Course, Lesson, UserProgress
from .serializers import CourseSerializer, LessonSerializer, UserProgressSerializer
from .ai_providers import ProviderRegistry
from .serializers import AskRequestSerializer, AskResponseSerializer

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user and request.user.is_authenticated

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@extend_schema(
    parameters=[
        OpenApiParameter(
            name="course",
            # description="ID курса, чтобы отфильтровать уроки данного курса",
            # required=False,
            # type=OpenApiTypes.INT,
            # location=OpenApiParameter.QUERY,
        )
    ]
)
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('course').all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        course_id = self.request.query_params.get('course')
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_lesson(request, pk: int):
    lesson = get_object_or_404(Lesson, pk=pk)
    try:
        progress = UserProgress.objects.create(user=request.user, lesson=lesson)
    except IntegrityError:
        progress = UserProgress.objects.get(user=request.user, lesson=lesson)
    return Response(UserProgressSerializer(progress).data, status=status.HTTP_200_OK)

def _parse_provider_list(s: str | None) -> list[str]:
    if not s:
        return []
    return [p.strip().lower() for p in s.split(",") if p.strip()]

@extend_schema(
    request=AskRequestSerializer,
    responses={200: AskResponseSerializer},
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ask_lesson(request, pk: int):
    lesson = get_object_or_404(Lesson, pk=pk)
    question = (request.data.get("question") or "").strip()

    # Список провайдеров по умолчанию (из .env или дефолт)
    default_chain = _parse_provider_list(os.getenv("DEFAULT_PROVIDERS")) or ["gigachat", "google"]

    # Если пользователь указал конкретный провайдер — ставим его первым и добавляем остальные как фолбэк
    requested = (request.data.get("provider") or request.query_params.get("provider") or "").strip().lower()
    if requested:
        chain = [requested] + [p for p in default_chain if p != requested]
    else:
        chain = default_chain

    if not question:
        return Response({"detail": "question is required"}, status=status.HTTP_400_BAD_REQUEST)

    context = (lesson.content or "").strip()[:8000]
    system_text = (
        "Ты — AI-репетитор. Дай развернутый, но четкий ответ, "
        "основанный только на предоставленном контексте. "
        "Если ответа в контексте нет, так и скажи: 'Ответ не найден в контексте.'"
    )
    fallback = "Ответ не найден в контексте."

    answer = ""
    provider_used = None
    errors = []

    for name in chain:
        try:
            provider = ProviderRegistry.create(name)
            text = provider.ask(context=context, question=question, system_text=system_text) or ""
            if text:
                answer = text
                provider_used = name
                break
            else:
                errors.append(f"{name}: empty")
        except Exception as e:
            errors.append(f"{name}: {type(e).__name__}")

    body = {"answer": answer or fallback, "provider": provider_used or chain[0]}
    # Для отладки
    if os.getenv("DEBUG", "False").lower() == "true":
        body["meta"] = {"chain": chain, "errors": errors}

    return Response(body, status=status.HTTP_200_OK)