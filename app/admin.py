# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Code


class CodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'read_count']
    search_fields = ['code']


admin.site.register(Code, CodeAdmin)
