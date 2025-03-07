from dataclasses import dataclass
from socket import gethostname
from typing import Any

import requests
from psutil import cpu_percent, virtual_memory

from config import config
from util import iso_time


@dataclass
class Device:
    name: str


@dataclass
class Metric:
    name: str
    value: float
    unit: str


@dataclass
class MetricSnapshot:
    device: Device
    timestamp: str
    metrics: list[Metric]


def local_snapshot() -> MetricSnapshot:
    """Retrieve a snapshot of the local machine's CPU and RAM usage."""

    # CPU % usage (1 sec. interval)
    cpu_usage: Metric = Metric(
        name="CPU Usage",
        value=cpu_percent(interval=1),
        unit="%",
    )

    # RAM usage (in MB)
    ram_usage: Metric = Metric(
        name="RAM Usage",
        value=virtual_memory().used / 1e6,
        unit="MB",
    )

    return MetricSnapshot(
        device=Device(name=gethostname()),
        timestamp=iso_time(),
        metrics=[cpu_usage, ram_usage],
    )


def remote_snapshot() -> MetricSnapshot:
    """Retrieve a snapshot of weather data from a remote weather API."""

    url: str = config.weather_endpoint.format(city=config.city, api_key=config.api_key)
    response: requests.Response = requests.get(url, timeout=10)
    data: Any = response.json()

    temp: float = float(data["main"]["temp"])
    humidity: float = float(data["main"]["humidity"])

    temperature: Metric = Metric(
        name="Temperature",
        value=temp,
        unit="°C",
    )

    humidity_metric: Metric = Metric(
        name="Humidity",
        value=humidity,
        unit="%",
    )

    return MetricSnapshot(
        device=Device(name=f"OpenWeather:{config.city}"),
        timestamp=iso_time(),
        metrics=[temperature, humidity_metric],
    )
