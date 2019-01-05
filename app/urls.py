from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import AddCodesView, CodeExportCsvView, CodeDetailAPIView

app_name = 'index'

urlpatterns = [
    url(r'^codes/add-multiple$', login_required(AddCodesView.as_view()), name='codes-add-multiple'),
    url(r'^codes/report/$', login_required(CodeExportCsvView.as_view()), name='codes-report'),
    url(r'^apiv1/codes/(?P<code>.*)/$', CodeDetailAPIView.as_view(), name='code-detail-api')
]
