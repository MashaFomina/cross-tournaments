from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Tournament


class TournamentTestCase(TestCase):
    urls = 'tournaments.test_urls'

    def setUp(self):
        self.tournament = Tournament.objects.create(start_date=timezone.now())

    def test_new_tournament_is_active(self):
        """Created tournament is active"""
        tournament = Tournament.objects.get(pk=self.tournament.pk)
        self.assertEqual(tournament.is_active(), True)

    def test_view_denies_anonymous(self):
        response = self.client.get(reverse('tournaments:list_tournaments', args=[]), follow=True)
        self.assertEqual(response.status_code, 401)
        response = self.client.post(reverse('tournaments:list_tournaments'), {})
        self.assertEqual(response.status_code, 401)

    # def test_call_view_loads(self):
    #     self.client.login(username='user', password='test')  # defined in fixture or with factory in setUp()
    #     response = self.client.get('/url/to/view')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'conversation.html')

    # def test_call_view_fails_blank(self):
    #     self.client.login(username='user', password='test')
    #     response = self.client.post('/url/to/view', {}) # blank data dictionary
    #     self.assertFormError(response, 'form', 'some_field', 'This field is required.')
    #     # etc. ...

    # def test_call_view_fails_invalid(self):
    #     # as above, but with invalid rather than blank data in dictionary

    # def test_call_view_fails_invalid(self):
    #     # same again, but with valid data, then
    #     self.assertRedirects(response, '/contact/1/calls/')