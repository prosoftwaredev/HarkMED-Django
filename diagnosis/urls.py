from django.conf.urls import url
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^$', views.DiagnosislistView.as_view(), name='diagnosis_list'),
    url(r'^diagnosis_thanks/$',
        TemplateView.as_view(template_name='diagnosis/diagnosis_thanks.html'),
        name='diagnosis_thanks'),
    url(r'^(?P<slug>[\w-]+)/$', views.DiagnosisView.as_view(),
        name='diagnosis'),
    url(r'^(?P<pk>\d+)/complete/$', views.complete_diagnosis,
        name="diagnosis_complete"),
]