from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from planetarium.models import PlanetariumDome, ShowTheme, AstronomyShow
from planetarium.serializers import AstronomyShowListSerializer, PlanetariumDomeSerializer, ShowThemeSerializer

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")
PLANETARIUM_DOME_URL = reverse("planetarium:planetariumdome-list")
SHOW_THEME_URL = reverse("planetarium:showtheme-list")


def sample_astronomy_show(**params):
    defaults = {
        "title": "Astronomy Show 1",
        "description": "Some description",
    }
    defaults.update(params)

    return AstronomyShow.objects.create(**defaults)


def sample_planetarium_dome(**params):
    defaults = {
        "name": "Planetarium Dome 1",
        "rows": 5,
        "seats_in_row": 10,
    }
    defaults.update(params)
    return PlanetariumDome.objects.create(**defaults)


def sample_show_theme(**params):
    defaults = {
        "name": "Show Theme 1",
    }
    defaults.update(params)
    return ShowTheme.objects.create(**defaults)


def detail_url(instance_id):
    return reverse("planetarium:astronomyshow-detail", args=[instance_id])


class UnauthenticatedShowsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_show_theme_auth_required(self):
        response = self.client.get(SHOW_THEME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_astronomy_show_auth_required(self):
        response = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_planetarium_dome_auth_required(self):
        response = self.client.get(PLANETARIUM_DOME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedShowsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_domes(self):
        sample_planetarium_dome()
        sample_planetarium_dome(name="Planetarium Dome 2")

        response = self.client.get(PLANETARIUM_DOME_URL)

        domes = PlanetariumDome.objects.all()
        serializer = PlanetariumDomeSerializer(domes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_dome_forbidden(self):
        payload = {
            "name": "Planetarium Dome 1",
            "rows": 5,
            "seats_in_row": 10,
        }

        response = self.client.post(PLANETARIUM_DOME_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_show_themes(self):
        sample_show_theme()
        sample_show_theme(name="Show Theme 2")

        response = self.client.get(SHOW_THEME_URL)

        show_themes = ShowTheme.objects.all()
        serializer = ShowThemeSerializer(show_themes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_shows(self):
        sample_astronomy_show()

        response = self.client.get(ASTRONOMY_SHOW_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_single_show(self):
        show = sample_astronomy_show()
        url = detail_url(show.id)

        response = self.client.get(url)
        serializer = AstronomyShowListSerializer(show)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_show_forbidden(self):
        show_theme = ShowTheme.objects.create(name="Show Theme 1")
        payload = {
            "title": "Astronomy Show 1",
            "description": "Some description",
            "show_theme": [show_theme.id],
        }

        response = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminShowsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="testpass123",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_dome_successful(self):
        payload = {
            "name": "Planetarium Dome 1",
            "rows": 3,
            "seats_in_row": 5,
        }

        response = self.client.post(PLANETARIUM_DOME_URL, payload)
        dome = PlanetariumDome.objects.get(id=response.data["id"])

        for key in payload:
            self.assertEqual(payload[key], getattr(dome, key))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_show_successful(self):
        show_theme = ShowTheme.objects.create(name="Show Theme 1")
        payload = {
            "title": "Astronomy Show 1",
            "description": "Some description",
            "show_theme": [show_theme.id],
        }

        response = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_show_invalid(self):
        payload = {
            "title": "",
            "description": "Some description",
        }

        response = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_show_successful(self):
        show = sample_astronomy_show()
        url = detail_url(show.id)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_show_theme_successful(self):
        payload = {
            "name": "Show Theme 3",
        }

        response = self.client.post(SHOW_THEME_URL, payload)
        show_theme = ShowTheme.objects.get(id=response.data["id"])

        for key in payload:
            self.assertEqual(payload[key], getattr(show_theme, key))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_show_theme_invalid(self):
        payload = {
            "name": "",
        }

        response = self.client.post(SHOW_THEME_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_show_theme_duplicate(self):
        sample_show_theme()
        payload = {
            "name": "Show Theme 1",
        }

        response = self.client.post(SHOW_THEME_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
