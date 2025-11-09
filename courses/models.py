from django.conf import settings
from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return f"{self.course}: {self.title}"

class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')


# Дополнительное задание

class GeneratedTask(models.Model):
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='generated_tasks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='generated_tasks')
    task_text = models.TextField()
    solution = models.TextField()
    student_answer = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Task#{self.id} lesson={self.lesson_id} user={self.user_id}'