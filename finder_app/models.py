from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    firstname = models.CharField(max_length=100, blank=True, null=True)
    middlename = models.CharField(max_length=100, blank=True, null=True)
    lastname = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    group_id = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'tbl_users'
        # Django doesn't natively support schemas in db_table for all backends in a simple way
        # but for PostgreSQL 'public.tbl_users' sometimes works or just 'tbl_users' if search_path is set.
        # However, to be explicit for the legacy DB:
        managed = False

    def get_full_name(self):
        return f"{self.firstname} {self.lastname}"

    def get_short_name(self):
        return self.firstname

class Roster(models.Model):
    entry_id = models.BigIntegerField(primary_key=True)
    hh_id = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=10, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    municipality = models.CharField(max_length=100, blank=True, null=True)
    barangay = models.CharField(max_length=100, blank=True, null=True)
    client_status = models.CharField(max_length=50, blank=True, null=True)
    hh_set = models.CharField(max_length=50, blank=True, null=True)
    prog = models.CharField(max_length=50, blank=True, null=True)
    relation_to_hh_head = models.CharField(max_length=100, blank=True, null=True)
    grantee = models.CharField(max_length=10, blank=True, null=True)
    member_status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"ds"."tbl_roster"' # Using double quotes for schema.table

class Config(models.Model):
    particular = models.CharField(max_length=255, primary_key=True)
    value = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_config'
