from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.models import  (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from djoser.signals import user_registered, user_activated


class UserAccountManager(BaseUserManager):

    RESTRICTED_USERNAMES = ['admin', 'undefined', 'null', 'superuser', 'root', 'system']
    
    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError('Users must have an email address.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        first_name = extra_fields.get('first_name', None)
        last_name = extra_fields.get('last_name', None)

        if not first_name or not last_name:
            raise ValueError('Users must have a first name and last name.')
        
        user.first_name = first_name
        user.last_name = last_name

        user_name = extra_fields.get('user_name', None)

        if user_name and user_name.lower() in self.RESTRICTED_USERNAMES:
            raise ValueError(f'The username {user_name} is not allowed.')
        
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_superuser = True
        user.save(using=self._db)

        return user
    

class UserAccount(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email
    

def post_user_registered(user, *args, **kwargs):
    print('User has been registered.')

def post_user_activated(user, *args, **kwargs):
    print('User has been activated.')


user_registered.connect(post_user_activated)
user_activated.connect(post_user_registered)
