from json import loads
from typing import TYPE_CHECKING, Any, Self

from cotc_common.metrics import JSONArr, ServerResponse
from flask import render_template, request
from requests import status_codes

from application.base import AppBase
from application.common import app_route, clear_scr, print_snapshots
from application.db import DB

if TYPE_CHECKING:
    from application.models import MetricSnapshot


class App(AppBase):
    db: DB

    def __init__(self: Self) -> None:
        super().__init__(__name__)
        self.db = DB(self)

    @app_route("/", "/latest")
    def route_latest(self: Self) -> str:
        with self.db:
            snapshots: list[MetricSnapshot] = self.db.get_snapshots(2, desc=True)
            print_snapshots(snapshots)
            return render_template("latest.html", snapshots=snapshots)

    @app_route("/all", "/history")
    def route_history(self: Self) -> str:
        with self.db:
            snapshots: list[MetricSnapshot] = self.db.get_snapshots(desc=True)
            return render_template("history.html", snapshots=snapshots)

    @app_route("/metrics", methods=["POST"])
    def route_json(self: Self) -> ServerResponse:
        data_list: Any = request.json
        json: JSONArr | Any = loads(data_list)

        clear_scr()
        self.logger.info("JSON data received")

        if not isinstance(json, list):
            return {"error": "Invalid JSON data"}, 400

        for snapshot in json:
            ret: ServerResponse = self.db.add_snapshot(snapshot)
            if ret[1] != status_codes.codes.ok:
                return ret

        return ret
