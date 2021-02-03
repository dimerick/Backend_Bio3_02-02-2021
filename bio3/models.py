from django.db import models
from django.contrib.gis.db import models as models_gis
from django.contrib.auth.models import UserManager, AbstractBaseUser
from bio3.storage_backends import MediaStorage

# Create your models here.
class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [email]

    objects = UserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

class Degree(models.Model):
    name = models.CharField(max_length=100, unique=True)

class FieldsOfStudy(models.Model):
    name = models.CharField(max_length=100, unique=True)

class University(models.Model):
    name = models.CharField(max_length=200)
    location = models_gis.PointField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, default='university')

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, primary_key=True, on_delete=models.CASCADE)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    field_of_study = models.ForeignKey(FieldsOfStudy, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    websites = models.CharField(max_length=1000, blank=True, null=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, blank=True, null=True)
    ind_researcher = models.BooleanField(default=False)
    

# class ProjectXUser(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = (('project', 'user'))

class Community(models.Model):
    name = models.CharField(max_length=200, unique=True)
    location = models_gis.PointField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location}"


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    created_by = models.ForeignKey(CustomUser, related_name="created_by", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    main_university = models.ForeignKey(University, related_name="main_university", on_delete=models.CASCADE)

    users = models.ManyToManyField(CustomUser, related_name='projects', blank=True)
    universities = models.ManyToManyField(University, related_name='projects', blank=True)
    communities = models.ManyToManyField(Community, related_name='projects', blank=True)
    researchers = models.ManyToManyField(Profile, related_name='researchers', blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (('name', 'created_by', 'main_university', 'is_active'))

class ProjectImage(models.Model):
    # image = models.FileField()
    image = models.FileField(storage=MediaStorage(), upload_to='projects/')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

# class ProjectXUniversityType(models.Model):
#     name = models.CharField(max_length=200)



# class ProjectXUniversity(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     university = models.ForeignKey(University, on_delete=models.CASCADE)
#     # project_x_university_type = models.ForeignKey(ProjectXUniversityType, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = (('project', 'university'))


# class ProjectXCommunity(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     community = models.ForeignKey(Community, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = (('project', 'community'))
