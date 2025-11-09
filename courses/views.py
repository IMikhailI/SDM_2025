from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, OpenApiParameter 
from drf_spectacular.types import OpenApiTypes
import json, os

from .models import Course, Lesson, UserProgress, GeneratedTask
from .serializers import CourseSerializer, LessonSerializer, UserProgressSerializer
from .ai_providers import ProviderRegistry, ask_ai, provider_chain
from .serializers import AskRequestSerializer, AskResponseSerializer
from .serializers import GeneratedTaskSerializer, CheckTaskRequestSerializer, CheckTaskResponseSerializer


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

@extend_schema(
    request=AskRequestSerializer,
    responses={200: AskResponseSerializer},
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ask_lesson(request, pk: int):
    lesson = get_object_or_404(Lesson, pk=pk)
    question = (request.data.get("question") or "").strip()

    chain = provider_chain(
        os.getenv("DEFAULT_PROVIDERS"),
        request.data.get("provider") or request.query_params.get("provider")
    )

    if not question:
        return Response({"detail": "question is required"}, status=status.HTTP_400_BAD_REQUEST)

    context = (lesson.content or "").strip()[:8000]
    system_text = (
        "Ты — AI-репетитор. Дай развернутый, но четкий ответ, "
        "основанный только на предоставленном контексте. "
        "Если ответа в контексте нет, так и скажи: 'Ответ не найден в контексте.'"
    )
    fallback = "Ответ не найден в контексте."

    text = ask_ai(
        prompt=question,
        providers=chain,
        system_text=system_text,
        context=context,
    )
    body = {"answer": text or fallback, "provider": chain[0]}
    return Response(body, status=status.HTTP_200_OK)


# Дополнительное задание

@extend_schema(
    tags=['lessons'],
    responses=GeneratedTaskSerializer,
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def generate_task(request, pk: int):
    lesson = get_object_or_404(Lesson, pk=pk)

    default_chain = provider_chain(os.getenv("DEFAULT_PROVIDERS"))
    override = (request.query_params.get('provider') or '').strip().lower()
    chain = [override] + [p for p in default_chain if p != override] if override else default_chain

    prompt = (
        f"Сгенерируй одну практическую задачу по теме: '{lesson.title}. {lesson.content}'. "
        "Задача должна быть уникальной и проверять понимание ключевых концепций. "
        "Уровень сложности - начальный. "
        "Предоставь также эталонное решение для проверки. "
        "Ответ верни строго в JSON с полями: task (строка), solution (строка)."
    )

    raw = ask_ai(prompt=prompt, providers=chain)

    task_text, solution = "", ""
    try:
        data = json.loads(raw)
        task_text = (data.get("task") or "").strip()
        solution  = (data.get("solution") or "").strip()
    except Exception:
        task_text = (raw or "").strip()
        solution = ""

    obj = GeneratedTask.objects.create(
        lesson=lesson,
        user=request.user,
        task_text=task_text,
        solution=solution,
    )
    return Response(GeneratedTaskSerializer(obj).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['tasks'],
    request=CheckTaskRequestSerializer,
    responses={"200": {"type": "object", "properties": {"id": {"type": "integer"}, "is_correct": {"type": "boolean"}}}},
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_task(request, pk: int):
    task = get_object_or_404(GeneratedTask, pk=pk, user=request.user)

    payload = CheckTaskRequestSerializer(data=request.data)
    payload.is_valid(raise_exception=True)
    student_answer = payload.validated_data["answer"]

    chain = provider_chain(os.getenv("DEFAULT_PROVIDERS"))

    prompt = (
        f"Сравни ответ студента '{student_answer}' с эталонным решением '{task.solution}'. "
        "Является ли ответ студента верным? Ответь ТОЛЬКО 'true' или 'false'."
    )
    raw = ask_ai(prompt=prompt, providers=chain)

    normalized = (raw or "").strip().lower()
    is_true  = ('true'  in normalized) and ('false' not in normalized)
    is_false = ('false' in normalized) and ('true'  not in normalized)
    is_correct = bool(is_true and not is_false)

    task.student_answer = student_answer
    task.is_correct = is_correct
    task.save(update_fields=["student_answer", "is_correct"])

    return Response({"id": task.id, "is_correct": is_correct}, status=status.HTTP_200_OK)