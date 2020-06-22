import os

from mapbox_tilesets.utils import validate_tileset_id
from mapbox_tilesets.scripts.cli import _get_token
from mapbox_tilesets.errors import TilesetsError


def test_get_token_parameter():
    assert _get_token(token='access_token') == 'access_token'


def test_get_token_environment_variables():
    os.environ["MAPBOX_ACCESS_TOKEN"] = 'access_token2'
    assert _get_token() == 'access_token2'
    del os.environ["MAPBOX_ACCESS_TOKEN"]

    os.environ["MapboxAccessToken"] = 'access_token3'
    assert _get_token() == 'access_token3'
    del os.environ["MapboxAccessToken"]


def test_get_token_raises():
    try:
        _get_token()
        assert False
    except TilesetsError as e:
        assert e.message == "No access token provided"


def test_validate_tileset_id():
    tileset = "iama.test"

    assert validate_tileset_id(tileset)


def test_validate_tileset_id_badfmt():
    tileset = "iama.test.ok"

    assert not validate_tileset_id(tileset)


def test_validate_tileset_id_toolong():
    tileset = "hellooooooooooooooooooooooooooooooo.hiiiiiiiuuuuuuuuuuuuuuuuuuuuuu"

    assert not validate_tileset_id(tileset)
