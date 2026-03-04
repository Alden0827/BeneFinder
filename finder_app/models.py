from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    group_id = models.IntegerField(blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, default='Enabled')

    def get_full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(filter(None, parts))

    def get_short_name(self):
        return self.first_name or self.username

    def __str__(self):
        return self.username

class Config(models.Model):
    particular = models.CharField(max_length=255, primary_key=True)
    value = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False  # keep False if table already exists
        db_table = 'tbl_config'

    def __str__(self):
        return self.particular