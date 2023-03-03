from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from orgs.models import Org
from questions.models import Question
from .models import Trash


class ApiTest(APITestCase):
    def setUp(self):
        self.user = user = get_user_model().objects.create_user('testing')
        self.org = Org.objects.create(title='testOrg', slug='testorg')
        self.org.staff_set.create(user=self.user, status='active')
        self.q = Question.objects.create(title='testQuestion')
        self.client.force_authenticate(user=user)

        self.q2 = q2 = Question.objects.create(title='testQuestion2')
        self.t = Trash.objects.create(
            content_type=ContentType.objects.get_for_model(q2),
            object_id=q2.pk,
            user=self.user,
            org=self.org
        )        

        
    def test_list_trash(self):
        r = self.client.get('/api/trash/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

        another_org = Org.objects.create(title='tset2', slug='tset2')
        r = self.client.get(f'/api/trash/?org={another_org.pk}')
        self.assertEqual(r.status_code, 400)

        r = self.client.get(f'/api/trash/?org={self.org.pk}')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        self.client.logout()
        r = self.client.get('/api/trash/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_with_wrong_org(self):
        another_org = Org.objects.create(title='tset2', slug='tset2')        
        r = self.client.post('/api/trash/', {
            'content_type': 'questions.question',
            'object_id': self.q.pk,
            'org': another_org.pk
        })
        self.assertEqual(r.status_code, 400)
        

    def test_create(self):
        q = self.q
        r = self.client.post('/api/trash/', {
            'content_type': 'questions.question',
            'object_id': q.pk,
            'org': self.org.pk
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        q.refresh_from_db()
        self.assertTrue(q.is_deleted)
        self.assertEqual(q.deleted_by, self.user)


    def test_delete(self):
        r = self.client.delete(f'/api/trash/{self.t.pk}/?org={self.org.pk}')
        self.assertEqual(r.status_code, 204)
        self.assertTrue(not Trash.objects.filter(pk=self.t.pk).exists())
        self.assertTrue(not Question.objects.filter(pk=self.q2.pk).exists())
        

    def test_cancel(self):
        q = self.q2
        r = self.client.post(f'/api/trash/{self.t.pk}/cancel/?org={self.org.pk}')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        q.refresh_from_db()
        self.assertTrue(not q.is_deleted)
        self.assertTrue(not Trash.objects.filter(pk=self.t.pk).exists())        
