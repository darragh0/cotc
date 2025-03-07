from dataclasses import dataclass
from json import load
from logging.config import dictConfig
from pathlib import Path
from typing import Final

ROOT_PATH: Final[Path] = Path(__file__).parent.parent
CONFIG_PATH: Final[Path] = ROOT_PATH / "config/config.json"


@dataclass
class AppConfig:
    weather_endpoint: str
    city: str
    api_key: str
    post_endpoint: str


def init_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        msg: str = f"Config file not found at {CONFIG_PATH!r}"
        raise FileNotFoundError(msg)

    with Path.open(CONFIG_PATH) as file:
        cfg: dict = load(file)

    log_cfg: dict = cfg["logging"]
    log_file_output: Path = ROOT_PATH / log_cfg["handlers"]["file"]["filename"]

    if not Path(log_file_output.parent).exists():
        Path(log_file_output.parent).mkdir(parents=True)

    log_cfg["handlers"]["file"]["filename"] = str(log_file_output)
    dictConfig(log_cfg)

    return AppConfig(**cfg["app"])


config: AppConfig = init_config()
