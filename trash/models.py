from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from orgs.models import Org


class WithTrashModel(models.Model):
    is_deleted = models.BooleanField('是否已删除', default=False)
    deleted_at = models.DateTimeField('删除时间', blank=True, null=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='+')
    
    class Meta:
        abstract = True


class Trash(models.Model):
    """通用回收站
    试题, 试卷等
    """
    # title = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, blank=True, null=True)
    org = models.ForeignKey(
        Org, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.content_object)

    class Meta:
        ordering = ['-created_at']
        unique_together = [['content_type', 'object_id']]
        indexes = [
            models.Index(fields=['content_type', 'object_id'])
        ]
