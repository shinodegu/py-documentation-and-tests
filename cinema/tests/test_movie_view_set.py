from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from rest_framework.reverse import reverse

from cinema.models import Movie, Genre, Actor
from cinema.serializers import MovieSerializer

MOVIES_URL = reverse("cinema:movie-list")


def sample_genre(name="Comedy"):
    return Genre.objects.create(name=name)

def sample_actor(first_name="Tom", last_name="Hanks"):
    return Actor.objects.create(first_name=first_name, last_name=last_name)

def sample_movie(**params):
    defaults = {
        "title": "Sample movie",
        "description": "Sample description",
        "duration": 90,
        "image": None,
    }
    defaults.update(params)

    return Movie.objects.create(**defaults)


class UnauthenticatedMovieApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(MOVIES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedMovieApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "testpassword123"
        )
        self.client.force_authenticate(self.user)

    def test_auth_required(self):
        response = self.client.get(MOVIES_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_movie_list(self):
        movie1 = sample_movie(title="Matrix")
        movie2 = sample_movie(title="Inception")

        res = self.client.get(MOVIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        titles = [m["title"] for m in res.data]
        self.assertIn(movie1.title, titles)
        self.assertIn(movie2.title, titles)

    def test_filter_movies_by_genres(self):
        genre1 = sample_genre(name="Action")
        genre2 = sample_genre(name="Drama")

        movie1 = sample_movie(title="Die Hard")
        movie2 = sample_movie(title="The Notebook")
        movie1.genres.add(genre1)
        movie2.genres.add(genre2)

        res = self.client.get(MOVIES_URL, {"genres": f"{genre1.id}"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], movie1.title)

    def test_filter_movies_by_actors(self):
        actor1 = sample_actor(first_name="Keanu", last_name="Reeves")
        actor2 = sample_actor(first_name="Ryan", last_name="Gosling")

        movie1 = sample_movie(title="Matrix")
        movie2 = sample_movie(title="Drive")
        movie1.actors.add(actor1)
        movie2.actors.add(actor2)

        res = self.client.get(MOVIES_URL, {"actors": f"{actor1.id}"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], movie1.title)

    def test_filter_movies_by_title(self):
        movie1 = sample_movie(title="Interstellar")
        movie2 = sample_movie(title="Tenet")

        res = self.client.get(MOVIES_URL, {"title": "stell"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], movie1.title)
