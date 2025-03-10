from __future__ import annotations

from typing import TYPE_CHECKING, Self

from cotc_common.metrics import (
    DeviceSchema,
    MetricSchema,
    MetricSnapshotSchema,
    ServerResponse,
    parse_snapshot_json,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

from application.models import Base, Device, Metric, MetricSnapshot

if TYPE_CHECKING:
    from types import TracebackType

    from cotc_common.metrics import JSONObj, MetricSnapshotJson
    from flask.ctx import AppContext

    from application.base import AppBase


class DB(SQLAlchemy):
    app: AppBase

    def __init__(self: Self, app: AppBase) -> None:
        super().__init__(app)
        self.app = app
        self.context: AppContext | None = None

        with self:
            Base.metadata.bind = self.engine
            Base.query = self.session.query_property()
            if self.app.debug:
                Base.metadata.create_all(self.engine)
            self.app.logger.info("Database initialized")

    def __enter__(self) -> AppContext:
        self.context = self.app.app_context()
        return self.context.__enter__()

    def __exit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.context is not None:
            self.context.__exit__(exc_type, exc_val, exc_tb)
        self.context = None

    def add_snapshot(self: Self, json_obj: JSONObj) -> ServerResponse:
        snapshot_json: MetricSnapshotJson | None = parse_snapshot_json(json_obj)

        if snapshot_json is None:
            self.app.logger.exception("Error parsing JSON data: Invalid JSON format")
            return {"status": "error", "message": "Invalid JSON data"}, 400

        device: Device | None = None
        snapshot_schema: MetricSnapshotSchema = MetricSnapshotSchema(
            device_id=0,
            timestamp=snapshot_json.timestamp,
            metrics=[],
        )

        try:
            with self:
                device = (
                    self.session.query(Device)
                    .filter_by(name=snapshot_json.device.name)
                    .first()
                )
                if device is not None:
                    snapshot_schema.device_id = int(device.id)

            if device is None:
                device_name: str = snapshot_json.device.name
                device_schema: DeviceSchema = DeviceSchema(name=device_name)
                device = Device.from_json(device_schema)
                with self:
                    self._addncommit(device)
                    snapshot_schema.device_id = int(device.id)

            snapshot: MetricSnapshot = MetricSnapshot.from_json(snapshot_schema)

            with self:
                self._addncommit(snapshot)
                for metric_data in snapshot_json.metrics:
                    metric_type: MetricSchema = MetricSchema(
                        name=metric_data.name,
                        value=metric_data.value,
                        unit=metric_data.unit,
                        snapshot_id=int(snapshot.id),
                    )
                    metric: Metric = Metric.from_json(metric_type)
                    self._addncommit(metric)

                    self.app.logger.info(
                        "JSON data saved to database: %s",
                        repr(snapshot),
                    )

        except OperationalError:
            self.app.logger.exception("Error saving JSON data to database")
            return {
                "status": "error",
                "message": "Error saving JSON data to database",
            }, 500

        return {"status": "success"}, 200

    def get_snapshots(
        self: Self,
        n: int | None = None,
        *,
        desc: bool = False,
    ) -> list[MetricSnapshot]:
        return (
            self.session.query(MetricSnapshot)
            .order_by(MetricSnapshot.id.desc() if desc else MetricSnapshot.id.asc())
            .limit(n)
            .all()
        )

    def _addncommit(self: Self, data: Metric | MetricSnapshot | Device) -> None:
        self.session.add(data)
        self.session.commit()
