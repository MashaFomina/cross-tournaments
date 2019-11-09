from django.contrib import admin


from .models import Tournament, Task, Hint


admin.site.register(Tournament)
admin.site.register(Task)
admin.site.register(Hint)
