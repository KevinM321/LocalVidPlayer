import yaml
import os


class Config:
    def __init__(self, data):
        for key, val in data.items():
            if isinstance(val, dict):
                setattr(self, key, Config(val))
            elif isinstance(val, list):
                setattr(self, key, [Config(v) if isinstance(v, dict) else v for v in val])
            else:
                setattr(self, key, val)


def load_config(path: str):
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}
    return Config(data)


# class Config:
#     def __init__(self, config_path=""):
#         self._config_path=config_path
#         self.load()
#
#     def load(self):
#         if not os.path.exists(self._config_path):
#             return 
#
#         with open(self._config_path, "r") as f:
#             data = yaml.safe_load(f) or {}
#
#         self.data = ConfigValue(data)
#
#     def save(self):
#         with open(self._config_path, "w") as f:
#             yaml.safe_dump(self._config, f)


# def singleton(cls):
#     _instances = {}
#     def wrapper(*args, **kwargs):
#         if cls not in _instances:
#             _instances[cls] = cls(*args, **kwargs)
#             return _instances[cls]
#         elif _instances[cls]._config_path ==
#     return wrapper
#     
#
# @singleton
# class BackEndConfig(BaseConfig):
#     def __init__(self, path):
#         super().__init__(path)
#
#
# class FrontEndConfig(BaseConfig):
#     _instance = None
#
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._instance._initialized = False
#         return cls._instance
#
#     def __init__(self, path):
#         if self._initialized:
#             return
#         self._initialized = True
#         super().__init__(path)
