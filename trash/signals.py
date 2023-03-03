import django.dispatch

# 取消删除, 从回收站恢复
cancel_delete = django.dispatch.Signal()

# 永久删除, 删除Trash和ContentObject
force_delete = django.dispatch.Signal()
