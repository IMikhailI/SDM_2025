import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_register_and_create_course():
    client = APIClient()
    r = client.post('/api/auth/register', {'username':'u1','password':'password123'}, format='json')
    assert r.status_code == 201
    r = client.post('/api/auth/token', {'username':'u1','password':'password123'}, format='json')
    assert r.status_code == 200
    token = r.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    rc = client.post('/api/courses/', {'title':'t','description':'d'}, format='json')
    assert rc.status_code == 201
