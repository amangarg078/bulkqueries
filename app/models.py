# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Code(models.Model):
    code = models.CharField(unique=True, max_length=14)
    read_count = models.IntegerField(default=0)

    def __unicode__(self):
        return self.code
