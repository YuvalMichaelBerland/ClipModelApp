from django.db import models
from django.contrib.auth.models import User

from storages.backends.s3boto3 import S3Boto3Storage

#class PublicMediaStorage(S3Boto3Storage):
#    location = "media"
#    default_acl = "public-read"
#    file_overwrite = False
#    custom_domain = False

class Category(models.Model):
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)

    def _str_(self):
        return self.name


class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(null=False, blank=False)#, upload_to='images/')
    description = models.TextField(null=True, blank=True)
    vector = models.JSONField(null=True, blank=True)

    def _str_(self):
        return self.description
