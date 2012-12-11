from os.path import exists, dirname, join, expanduser, isdir
from os import makedirs
from errno import EEXIST
from logging import getLogger
from sys import version_info
from tranny.exceptions import ConfigError

try:
    from configparser import ConfigParser, NoOptionError, NoSectionError
except ImportError:
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError

if version_info >= (3, 2):
    def mkdirp(path):
        return makedirs(path, exist_ok=True)
else:
    def mkdirp(path):
        try:
            makedirs(path)
        except OSError as err: # Python >2.5
            if err.errno == EEXIST and isdir(path):
                pass
            else:
                raise

class Configuration(ConfigParser):
    def __init__(self):
        ConfigParser.__init__(self)
        self.log = getLogger('tranny.config')

    def rules(self):
        pass

    def find_config(self, config_name="tranny.ini"):
        """ Attempt to find a configuration file to load. This function first attempts
         the users home directory standard location (~/.config/tranny). If that fails it
         moves on to configuration files in the source tree root directory.

        :param config_name:
        :type config_name:
        :return:
        :rtype:
        """
        # Try and get home dir config
        home_config = expanduser("~/.config/tranny/{0}".format(config_name))
        if exists(home_config):
            return home_config

        # Try and get project source root config
        base_path = dirname(dirname(__file__))
        config_path = join(base_path, config_name)
        if exists(config_path):
            return config_path

        # No configs were found
        return False

    def create_dirs(self, path="~/.tranny"):
        """ Initialize a users config directory by creating the prerequisite directories.

        :return:
        :rtype:
        """
        config_path = expanduser(path)
        if not exists(config_path):
            mkdirp(config_path)
            self.log.info("Create new configuration path: {0}".format(config_path))

    def initialize(self, file_path=False):
        self.create_dirs()
        if not file_path:
            file_path = self.find_config()
        try:
            self.read(file_path)
        except OSError:
            raise ConfigError("No suitable configuration found")

    def find_sections(self, prefix):
        sections = [section for section in self.sections() if section.startswith(prefix)]
        return sections

    @property
    def rss_feeds(self):
        return map(self.get_feed_config, self.find_sections("rss_"))

    def get_feed_config(self, section, def_interval=300):
        try:
            name = self.get(section, "name")
        except NoOptionError:
            name = section.split("_", 1)[1]
        try:
            interval = self.getint(section, "interval")
        except NoOptionError:
            interval = def_interval
        rss_conf = {
            'name': name,
            'interval': interval,
            'enabled': self.getboolean(section, "enabled"),
            'url': self.get(section, "url")
        }
        return rss_conf

    def build_regex_fetch_list(self, section=None, key_name="shows"):
        """
        unused?

        :param section:
        :type section:
        :param key_name:
        :type key_name:
        :return:
        :rtype:
        """
        from tranny.parser import normalize
        if section:
            name_list = [normalize(name) for name in self.get(section, key_name).split(",")]
        else:
            name_list = [self.build_regex_fetch_list(s, key_name) for s in self.find_sections("section_")]
        return name_list

    @staticmethod
    def get_unique_section_name(section_name, sep="_"):
        try:
            return sep.join(section_name.split(sep)[1:])
        except Exception:
            return section_name





