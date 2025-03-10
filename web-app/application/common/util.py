from datetime import datetime as dt
from datetime import timezone as tz
from functools import wraps
from typing import Any, Callable

from flask import current_app


def app_route(*args: str, **kwargs: Any) -> Callable:  # noqa: ANN401
    def decorator(func: Callable) -> Callable:
        func.routes = args  # type: ignore[attr-defined]
        func.kwargs = kwargs  # type: ignore[attr-defined]

        @wraps(func)
        def wrapper(self: Any) -> str:  # noqa: ANN401
            current_app.logger.info("Route accessed: %s", args)
            return func(self)

        return wrapper

    return decorator


def utc_now() -> dt:
    return dt.now(tz.utc)
