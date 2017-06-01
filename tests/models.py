from django.db import models as django_models
from django.test import TestCase, mock
from django.contrib.contenttypes.models import ContentType

from .. import models
from .. import settings

from .utils import get_image_in_memory_data

class BaseTestModel(django_models.Model):
    name = django_models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class TestModel(models.ContentGalleryMixin, BaseTestModel):
    pass


class AnotherTestModel(models.ContentGalleryMixin, BaseTestModel):
    gallery_visible = False


class WrongTestModel(BaseTestModel):
    pass


class ImageTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        clean_db()
        cls.object = TestModel.objects.create(name="TestObject")

    @mock.patch('gallery.models.slugify_unique', return_value='foo')
    def setUp(self, slugify_unique):
        self.image = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=self.object.id
        )
        self.image = self.get_image()

    def tearDown(self):
        self.image.delete()

    @classmethod
    def tearDownClass(cls):
        cls.object.delete()

    @staticmethod
    def get_image():
        return models.Image.objects.all()[0]

    @staticmethod
    def get_name(name):
        return "/".join([settings.GALLERY_PATH, name])


class MultipleObjectsImageTestCase(ImageTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.second_object = TestModel.objects.create(
            name="SecondTestObject"
        )
        cls.another_object = AnotherTestModel.objects.create(
            name="AnotherTestObject"
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.second_object.delete()
        cls.another_object.delete()


class ViewsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        clean_db()
        cls.ctype = ContentType.objects.get_for_model(TestModel)
        cls.object = TestModel.objects.create(name="Test object")
        cls.image1 = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=0,
            content_type=cls.ctype,
            object_id=cls.object.id
        )
        cls.image2 = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=1,
            content_type=cls.ctype,
            object_id=cls.object.id
        )
        cls.alone_object = TestModel.objects.create(
            name="Alone test object"
        )

    @classmethod
    def tearDownClass(cls):
        cls.image1.delete()
        cls.image2.delete()
        cls.object.delete()
        cls.alone_object.delete()


class AjaxRequestMixin:

    def send_ajax_request(self, url):
        return self.client.get(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )


def clean_db():
    TestModel.objects.all().delete()
    AnotherTestModel.objects.all().delete()
    WrongTestModel.objects.all().delete()
    models.Image.objects.all().delete()
