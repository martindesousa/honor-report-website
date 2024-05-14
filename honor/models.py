import enum

from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone

class Task(models.Model):
    description = models.TextField(max_length=200, null=True)

    def __str__(self):
        return self.description

# citation: https://medium.com/@bencleary/using-enums-as-django-model-choices-96c4cbb78b2e
class ResolutionStatus(enum.IntEnum):
    NEW = 1
    IN_PROGRESS = 2
    RESOLVED = 3

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Report(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=40, blank=True)
    timeStamp = models.DateTimeField(default=django.utils.timezone.now)
    nameOfOffender = models.CharField(max_length=200)
    className = models.CharField(max_length=300)
    location = models.CharField(max_length=300)
    description = models.TextField()
    file = models.FileField(upload_to='report/', blank=True, null=True)
    addInfo = models.TextField()
    status = models.IntegerField(choices=ResolutionStatus.choices(), default=ResolutionStatus.NEW)
    admin_comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nameOfOffender} {self.className} {self.location} {self.description} {self.file}"

    def get_status(self):
        return ResolutionStatus(self.status).name
