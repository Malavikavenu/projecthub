from django.contrib import admin

# Register your models here.


from store.models import Tag,Project,OrderSummary

admin.site.register(Tag)

admin.site.register(Project)

admin.site.register(OrderSummary)
