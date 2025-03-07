from dataclasses import asdict
from json import dumps
from typing import Final

from requests import post
from requests.models import Response
from rich import print as rprint

from config import config
from metrics import MetricSnapshot

JSON_HEADER: Final[dict[str, str]] = {"Content-Type": "application/json"}


class SnapshotPublisher:
    def send_snapshots(self, *snapshots: MetricSnapshot) -> Response:
        rprint(dumps([asdict(s) for s in snapshots]))
        return post(
            url=config.post_endpoint,
            headers=JSON_HEADER,
            json=dumps([asdict(s) for s in snapshots]),
            timeout=10,
        )


__all__: list[str] = ["SnapshotPublisher"]
