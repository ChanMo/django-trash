from django.contrib.contenttypes.models import ContentType
from trash.models import Trash

def move_to_trash(obj, user, org=None):
    contenttype = ContentType.objects.get_for_model(obj)
    return Trash.objects.create(
        content_type = contenttype,
        object_id = obj.pk,
        user = user,
        org = org
    )
