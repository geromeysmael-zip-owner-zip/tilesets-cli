"""tilesets package"""

__version__ = "0.3.1"
import requests

from tilesets.utils import _get_token
from tilesets.errors import TilesetsError


class MapboxTilesetSession:
    def __init__(self, mapbox_token=None, mapbox_api="https://api.mapbox.com"):
        self.mapbox_token = _get_token(mapbox_token)
        self.mapbox_api = mapbox_api
        self.url_config = dict(
            create_tileset=f"{mapbox_api}/tilesets/v1/{{tileset_id}}?access_token={mapbox_token}",
            list_tilesets=f"{mapbox_api}/tilesets/v1/{{username}}?access_token={mapbox_token}",
            validate_recipe=f"{mapbox_api}/tilesets/v1/validateRecipe?access_token={mapbox_token}",
            status=f"{mapbox_api}/tilesets/v1/{{tileset_id}}/status?access_token={mapbox_token}",
        )

    def create_tileset(self, tileset_id, recipe, name="", description="", private=True):
        """Create a new tileset with a recipe

        Parameters
        ----------
        tileset_id: str
            tileset_id in the form of {username}.{tileset handle}
        recipe: dict
            recipe json document
        name: str
            name of the tileset
            default=""
        description: str
            description of the tileset
            default=""
        private: bool
            set the tileset privacy to private
            default=True

        Returns
        -------
        api_response: dict
            json object from api response
        """
        body = dict(description=description, name=name, recipe=recipe)

        if private:
            body.update(private=private)

        url = self.url_config["create_tileset"].format(tileset_id=tileset_id)

        resp = requests.post(url, json=body)

        if resp.status_code == 200:
            return Tileset(id=name, description=description, recipe=recipe)
        else:
            raise TilesetsError(resp.text)

    def validate_recipe(self, recipe):
        """"""
        url = self.url_config["validate_recipe"]
        resp = requests.put(url, json=recipe)

        if resp.status_code == 200:
            return resp.json()
        else:
            raise TilesetsError(resp.text)

    def list_tilesets(self, username):
        """For a given account, return an iterable of tilesets

        Parameters
        ----------
        username: str
            mapbox username

        Returns
        -------
        tilesets: generator of dicts
            iterable generator of tilesets
        """
        url = self.url_config["list_tilesets"].format(username=username)

        resp = requests.get(url)

        if resp.status_code == 200:
            r_json = resp.json()
            for r in r_json:
                yield Tileset(**r)

            while "next" in resp.links:
                link_url = resp.links["next"]["url"]
                resp = requests.get(f"{link_url}&access_token={self.mapbox_token}")
                r_json = resp.json()
                for r in r_json:
                    yield Tileset(**r)
        else:
            raise TilesetsError(resp.text)

    def status(self, tileset_id):
        url = self.url_config["status"].format(tileset_id=tileset_id)
        resp = requests.get(url)

        if resp.status_code == 200:
            return resp.json()
        else:
            raise TilesetsError(resp.text)


class Tileset:
    """Abstraction class for Tilesets
    """

    def __init__(
        self,
        id=None,
        type=None,
        name=None,
        center=None,
        created=None,
        modified=None,
        visibility=None,
        description=None,
        filesize=None,
        status=None,
        recipe=None,
        mapbox_session=None,
        **kwargs,
    ):
        self.id = id
        self.type = type
        self.name = name
        self.center = center
        self.created = created
        self.modified = modified
        self.visibility = visibility
        self.description = description
        self.filesize = filesize
        self.status = status
        self.mapbox_session = None
        self._serializable = [
            "id",
            "type",
            "name",
            "center",
            "created",
            "modified",
            "visibility",
            "description",
            "filesize",
            "status",
        ]

    def _set_session(self, mapbox_session, mapbox_token, mapbox_api):
        if mapbox_session is None:
            if mapbox_token is None:
                raise TilesetsError("Token must be provided")
            self.mapbox_session = MapboxTilesetSession(mapbox_token, mapbox_api)
        else:
            self.mapbox_session = mapbox_session

    def to_dict(self):
        return {
            a: self.__dict__[a]
            for a in self._serializable
            if self.__dict__[a] is not None
        }

    def get_status(self, mapbox_session=None, mapbox_token=None, mapbox_api=None):
        self._set_session(mapbox_session, mapbox_token, mapbox_api)

        return self.mapbox_session.get_status(self.id)
