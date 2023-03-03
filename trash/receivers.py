from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from .signals import cancel_delete, force_delete
from .models import Trash


@receiver(post_save, sender=Trash)
def set_deleted(sender, instance=None, created=False, **kwargs):
    """Content移入回收站/删除"""
    if not created:
        return

    obj = instance.content_object
    obj.is_deleted = True
    obj.deleted_at = timezone.now()
    obj.deleted_by = instance.user
    obj.save()


@receiver(force_delete)
def delete_obj(sender, instance=None, **kwargs):
    """从回收站删除, 彻底删除"""
    instance.content_object.delete()


@receiver(cancel_delete)
def cancel_delete(sender, instance=None, **kwargs):
    """取消删除, 从回收站恢复"""
    obj = instance.content_object
    obj.is_deleted = False
    obj.deleted_at = None
    obj.deleted_by = None
    obj.save()

    instance.delete()
