from django.contrib import admin
from .models import Course, Lesson, UserProgress
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(UserProgress)
