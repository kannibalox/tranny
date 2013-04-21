import re
from logging import getLogger
import httplib
from requests import Session
from requests.auth import HTTPBasicAuth
from tranny import TrannyException


class uTorrentException(TrannyException):
    pass


class InvalidToken(uTorrentException):
    pass


class url_args(dict):
    def __str__(self):
        return "&".join(["{0}={1}".format(k, v) for k, v in self.items()])


class UTorrentClient(object):
    """
    A basic uTorrent WebUI API client
    """
    _config_key = "utorrent"
    _url_prefix = "/gui"
    version = None
    _token = False

    def __init__(self, config, host=None, port=None, user=None, password=None):
        """ Setup the connection parameters and verify connection

        :param config: Tranny configuration
        :type config: tranny.configuration.Configuration
        :param host: uTorrent webui host
        :type host: str
        :param port: webui port
        :type port: int
        :param user: webui username
        :type user: str
        :param password: webui password
        :type password: str
        """
        self.log = getLogger("rpc.utorrent")
        if not host:
            host = config.get_default(self._config_key, "host", "localhost")
        self.host = host
        if not port:
            port = config.getint(self._config_key, "port")
        self.port = port
        if not user:
            user = config.get_default(self._config_key, "user", None)
        self.user = user
        if not password:
            password = config.get_default(self._config_key, "password", None)
        self.password = password
        self._session = Session()
        version = self.get_version()
        self.log.info("Connected to uTorrent build {0}".format(version))

    def _fetch(self, url="/", args=None, json=True, token=True, resend=False):
        """ Fetch data from the uTorrent API.

        :param url: URL to request. The self._urlprefix value will be prefixed to this value
        :type url: str
        :param args: dict of url keyword arguments
        :type args: dict
        :param json: Should the request be decoded as json
        :type json: bool
        :param token: Send the AuthToken along with the request?
        :type token: bool
        :param resend: Is this a second attempt to handle a new token
        :type resend: bool
        :return: server response
        :rtype: str, dict
        """
        url = "http://{0}:{1}{2}{3}".format(self.host, self.port, self._url_prefix, url)
        full_args = url_args()
        if token:
            full_args['token'] = self.token
        if args:
            full_args.update(args)
        if full_args:
            url = "{0}?{1}".format(url, full_args)
        result = self._session.get(url, auth=HTTPBasicAuth(self.user, self.password))
        if result.status_code == httplib.MULTIPLE_CHOICES:  # 300
            if resend:
                raise InvalidToken("Unable to fetch new AuthToken")
            return self._fetch(url, args=args, json=json, token=token, resend=True)
        if result and not json:
            result = result.content
        elif result and json:
            try:
                result = result.json
            except Exception as err:
                self.log.exception("Failed to decode response to json")
                raise
        return result

    @property
    def token(self, force_update=False):
        """ Fetch the AuthToken from the API

        :param force_update: Force a refresh of the current API token
        :type force_update: bool
        :return: Token parsed from page
        :rtype: str
        """
        if not self._token or force_update:
            body = self._fetch("/token.html", json=False, token=False)
            match = re.search(r"<div id='token' style='display:none;'>([^<>]+)</div>", body, re.I | re.M)
            if not match:
                raise AttributeError("Failed to find utorrent token")
            token = match.group(1)
            assert len(token) == 64, "Invalid token received"
            self._token = token
        return self._token

    def get_version(self):
        """ Fetch the version (build) of utorrent connected.

        :return: Connected uTorrent build number
        :rtype: int
        """
        if not self.version:
            response = self._fetch(args={'action': "getsettings"})
            version = response["build"]
            self.version = version
        return self.version
