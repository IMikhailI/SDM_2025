from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import RegisterRequestSerializer, RegisterResponseSerializer

@extend_schema(
    tags=['auth'],
    request=RegisterRequestSerializer,
    responses={201: RegisterResponseSerializer, 400: None}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'detail': 'username/password required'}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 8:
        return Response({'detail': 'password must be >= 8 chars'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'detail': 'username taken'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, password=password)
    return Response({'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)
