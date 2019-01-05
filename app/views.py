# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv

from django.core.urlresolvers import reverse
from django.http import StreamingHttpResponse
from django.views.generic import View
from django.views.generic.edit import FormView
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics, serializers


from .models import Code
from .forms import CodeForm
from .serializers import CodeSerializer

# Create your views here.


class Echo(object):
    """An object that implements just the write method of the file-like interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class CodeExportCsvView(View):

    def get(self, request, *args, **kwargs):
        codes = Code.objects.filter(read_count__gt=0)  # Get only the codes having read_count > 0
        headers = ['code', 'read_count']

        def get_row(obj):
            row = [obj.code.encode("utf-8"), obj.read_count]
            return row

        def stream(headers, data):  # Helper function to inject headers
            if headers:
                yield headers
            for obj in data:
                yield get_row(obj)
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in stream(headers, codes)),
            content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="codes.csv"'
        return response


class AddCodesView(FormView):
    form_class = CodeForm
    template_name = "add-codes.html"

    def form_valid(self, form):
        total_codes = form.cleaned_data.get('total_codes_to_generate')
        code_length = getattr(settings, 'CODE_LENGTH', 14)
        codes = []
        for _ in range(total_codes):
            codes.append(get_random_string(length=code_length))

        codes = set(codes)
        codes_in_db = Code.objects.filter(code__in=codes).values_list('code', flat=True)
        codes_not_in_db = codes - set(codes_in_db)
        code_obj_list = []
        for code in codes_not_in_db:
            code_obj_list.append(Code(code=code))

        Code.objects.bulk_create(code_obj_list)
        messages.success(self.request, "Codes imported successfully")
        return super(AddCodesView, self).form_valid(form)

    def get_success_url(self):
        return reverse("admin:app_code_changelist")


class CodeDetailAPIView(generics.RetrieveAPIView):
    queryset = Code.objects.all()
    serializer_class = CodeSerializer
    lookup_field = 'code'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        obj.read_count += 1
        obj.save()

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
