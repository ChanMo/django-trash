from django.views.generic import DeleteView
from django.db.models import Count
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.core.paginator import Paginator
from django.urls import reverse
from django_filters.views import FilterView
from .models import Trash
from .signals import force_delete, cancel_delete


class TrashAdminView(LoginRequiredMixin, FilterView):
    """回收站后台"""
    model = Trash
    filterset_fields = ('content_type',)
    paginate_by = 12
    template_name = 'admin/trashs/trash/trash.html'
    content_type_list = []
    contenttype = None
    search = None

    def dispatch(self, request, *args, **kwargs):
        self.search = self.request.GET.get('search', '')
        page = self.request.GET.get('page', 1)
        qs = Trash.objects.values('content_type').annotate(Count('content_type')).order_by('-content_type__count')
        self.content_type_list = [ContentType.objects.get_for_id(i['content_type']) for i in qs]
        self.contenttype = int(request.GET.get('content_type', 0))
        # 跳转一个conten_type标签页面
        if (not self.contenttype or self.contenttype not in [i['content_type'] for i in qs]) and qs:
            url = reverse('admin_trash')
            return redirect(f'{url}?content_type={qs[0]["content_type"]}&search={self.search}&page={page}')
        return super().dispatch(request, *args, **kwargs)
    
    
    def get_queryset(self):
        qs = super().get_queryset().filter(org__isnull=True, user=self.request.user)
        if not self.search:
            return qs
        contenttype = ContentType.objects.get(pk=self.contenttype)
        # if contenttype.app_label == 'questions' and contenttype.model == 'question':
        #     questions = Question.objects.filter(title__contains=self.search, is_deleted=True)
        #     qs = qs.filter(object_id__in=questions)

        return qs   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_type_list'] = self.content_type_list
        context['search'] = self.search
        context = {**context, **admin.site.each_context(self.request)}
        return context
        

        
class CancelAdminDeleteView(LoginRequiredMixin, DeleteView):
    """ 后台回收站恢复"""
    model = Trash
    template_name = 'admin/trashs/trash/cancel.html'

    def get_success_url(self):
        # 成功后跳转路径
        return reverse('admin_trash')

    def get_queryset(self):
        return super().get_queryset().filter(org__isnull=True, user=self.request.user)

    def form_valid(self, form):
        cancel_delete.send(self.__class__, instance=self.get_object())
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {**context, **admin.site.each_context(self.request)}
        return context


class ForceAdminDeleteView(LoginRequiredMixin, DeleteView):
    """ 后台永久删除 """
    model = Trash
    template_name = 'admin/trashs/trash/permanent_delete.html'

    def get_success_url(self):
        # 成功后跳转路径
        return reverse('admin_trash')

    def get_queryset(self):
        return super().get_queryset().filter(org__isnull=True, user=self.request.user)

    def form_valid(self, form):
        force_delete.send(self.__class__, instance=self.get_object())
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {**context, **admin.site.each_context(self.request)}
        return context
