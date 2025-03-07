from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ValidationError

if TYPE_CHECKING:
    from cotc_common.metrics._types import JSONObj


class MetricJson(BaseModel):
    name: str
    value: float
    unit: str


class MetricSchema(BaseModel):
    name: str
    value: float
    unit: str
    snapshot_id: int


class DeviceJson(BaseModel):
    name: str


class DeviceSchema(BaseModel):
    name: str


class MetricSnapshotJson(BaseModel):
    device: DeviceJson
    timestamp: str
    metrics: list[MetricJson]


class MetricSnapshotSchema(BaseModel):
    device_id: int
    timestamp: str
    metrics: list[MetricSchema]


def parse_snapshot_json(json: JSONObj) -> MetricSnapshotJson | None:
    try:
        return MetricSnapshotJson(**json)
    except ValidationError:
        return None
