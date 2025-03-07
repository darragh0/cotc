from datetime import datetime as dt
from datetime import timezone as tz


def iso_time() -> str:
    return dt.now(tz=tz.utc).isoformat()


__all__: list[str] = ["iso_time"]
