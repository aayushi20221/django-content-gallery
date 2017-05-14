from django import forms

from . import models
from . import widgets

class ImageAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        super(ImageAdminForm, self).__init__(*args, **kwargs)
        try:
            model_class = self.instance.content_type.model_class()
        except:
            model_class = None
        if initial and initial.get('_popup'):
            self.fields['content_type'].widget = forms.HiddenInput()
            self.fields['object_id'].widget = forms.HiddenInput()
        else:
            self.fields['object_id'].widget.model_class = model_class

    def clean(self):
        cleaned_data = super().clean()
        if self.is_bound:
            try:
                ctype = cleaned_data.get('content_type')
                model_class = ctype.model_class()
                self.fields['object_id'].widget.model_class = model_class
            except:
                pass
        return cleaned_data

    class Meta:
        model = models.Image
        fields = ('image', 'content_type', 'object_id')
        widgets = {
            'image': widgets.ImageWidget,
            'content_type': widgets.ContentTypeSelect,
            'object_id': widgets.ObjectIdSelect,
        }


class ImageAdminInlineForm(forms.ModelForm):
    class Meta:
        widgets = {
            'position': forms.HiddenInput(attrs={'class': 'content-gallery-image-position'}),
            'image': widgets.ImageInlineWidget()
        }
