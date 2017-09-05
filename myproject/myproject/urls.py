from django.conf.urls import url
from django import forms
from django.views.generic.base import TemplateView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import renderers

#
# Godawful patch...  If this is turned on. The problem no longer
# occurs.
#
if False:
    oldGetState = Response.__getstate__

    def newGetState(self):
        state = oldGetState(self)
        for key in ('data', ):
            if key in state:
                del state[key]
        return state

    Response.__getstate__ = newGetState


class ContextTemplateView(TemplateView):
    context = None

    def get_context_data(self, **kwargs):
        context = super(ContextTemplateView, self).get_context_data(**kwargs)
        if self.context is not None:
            context.update(self.context)
        return context

class MyForm(forms.Form):
    # This field must be present for the issue to occur.
    heading = forms.CharField()

class RestView(GenericAPIView):
    renderer_classes = (renderers.TemplateHTMLRenderer, )

    def get(self, request):
        return Response({"form": MyForm()}, content_type="text/html",
                        template_name="home.html")

urlpatterns = [
    url(r'^$', RestView.as_view()),
    # This view won't generate the issue.
    url(r'foo$', ContextTemplateView.as_view(template_name="home.html",
                                             context={"form": MyForm()})),
]
