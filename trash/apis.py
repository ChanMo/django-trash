from django.shortcuts import get_object_or_404
from django.core.exceptions import BadRequest
from django.http import HttpResponseForbidden
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet

from orgs.models import Org
from .models import Trash
from .serializers import TrashSerializer
from .signals import cancel_delete, force_delete


class TrashViewSet(CreateModelMixin,
                   ListModelMixin,
                   DestroyModelMixin,
                   GenericViewSet):
    serializer_class = TrashSerializer
    queryset = Trash.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ('content_type', 'org')

    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            raise ValidationError(e)


    def get_queryset(self):
        qs = super().get_queryset()
        # qs = qs.filter(user=self.request.user)
        org_id = int(self.request.GET.get('org', 0))
        if not org_id and self.request.user.is_staff:
            # admin user
            return qs.filter(org__isnull=True)

        org = get_object_or_404(Org, pk=org_id)
        
        my_orgs = self.request.user.get_orgs()
        if org_id not in [i.id for i in my_orgs]:
            # if not my orgs
            raise BadRequest()

        qs = qs.filter(org=org)
        return qs


    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        obj = self.get_object()
        cancel_delete.send(self.__class__, instance=obj)
        return Response({'success':True})


    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        force_delete.send(self.__class__, instance=obj)
        return super().destroy(request, *args, **kwargs)

        

router = DefaultRouter()
router.register('', TrashViewSet)

urlpatterns = router.urls
