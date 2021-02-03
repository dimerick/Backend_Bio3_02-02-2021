from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


# class StaticStorage(S3Boto3Storage):
#     location = settings.AWS_STATIC_LOCATION
#     default_acl = 'public-read'


class MediaStorage(S3Boto3Storage):
    location = settings.AWS_PUBLIC_MEDIA_LOCATION
    default_acl = 'public-read'
    file_overwrite = False


# class PrivateStorage(S3Boto3Storage):
#     location = settings.AWS_PRIVATE_MEDIA_LOCATION
#     default_acl = 'private'