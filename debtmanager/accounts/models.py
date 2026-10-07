import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

def generate_uuid7():
    return uuid.uuid7()

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=generate_uuid7, editable=False)