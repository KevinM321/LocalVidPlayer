import yaml
import os
from abc import ABC, abstractmethod


# change to your own configuration file path
BACKEND_CONFIG_PATH = "config/backend_conf.yaml"
FRONTEND_CONFIG_PATH = "config/frontend_conf.yaml"


class BaseConfig(ABC):
    def __init__(self, config_path=""):
        self._config_path=config_path
        self._config = {}
        self.load()
        self.test = 0

    def load(self):
        if not os.path.exists(self._config_path):
            return 

        with open(self._config_path, "r") as f:
            self._config = yaml.safe_load(f) or {}

    def save(self):
        with open(self._config_path, "w") as f:
            yaml.safe_dump(self._config, f)

    def get(self, *keys : str):
        try:
            curr = self._config
            for key in keys:
                curr = curr[key]
        except:
            return None
        return curr;

    def set(self, value, *keys : list) -> bool:
        print(os.getcwd())
        if len(keys) == 0:
            return True

        print(self._config)
        try:
            curr = self._config
            for key in keys:
                print(curr)
                curr = curr[key]
        except:
            return False
        return True
    

class BackEndConfig(BaseConfig):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__(BACKEND_CONFIG_PATH)


class FrontEndConfig(BaseConfig):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__(FRONTEND_CONFIG_PATH)
