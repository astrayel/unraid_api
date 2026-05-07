"""Helpers."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from aiohttp import ClientConnectionError, ClientConnectorSSLError
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .exceptions import GraphQLError, GraphQLMultiError, GraphQLUnauthorizedError
from .models import ContainerHealth

if TYPE_CHECKING:
    from collections.abc import Callable

_LOGGER = logging.getLogger(__name__)


def error_handler[T](func: Callable[[], T]) -> Callable:
    """Handle API errors and raise HomeAssistantError."""

    async def decorated(*args: tuple[Any], **kwargs: dict[str, Any]) -> T:
        try:
            return await func(*args, **kwargs)
        except ClientConnectorSSLError as exc:
            _LOGGER.debug("Button: SSL error: %s", str(exc))
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="ssl_error",
                translation_placeholders={"error": str(exc)},
            ) from exc
        except (ClientConnectionError, TimeoutError) as exc:
            _LOGGER.debug("Button: Connection error: %s", str(exc))
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="cannot_connect",
                translation_placeholders={"error": str(exc)},
            ) from exc
        except GraphQLUnauthorizedError as exc:
            _LOGGER.debug("Button: Auth failed")
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="auth_failed",
                translation_placeholders={"error_msg": str(exc)},
            ) from exc
        except (GraphQLError, GraphQLMultiError) as exc:
            _LOGGER.debug("Button: GraphQL Error response: %s", str(exc))
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="error_response",
                translation_placeholders={"error_msg": str(exc)},
            ) from exc

    return decorated


_HEALTH_RE = re.compile(r"\((healthy|unhealthy|health: starting)\)")
_UPTIME_NUMBER_RE = re.compile(
    r"^Up\s+(?:Less than\s+a\s+(?P<lunit>second|minute|hour|day)"
    r"|About\s+a[n]?\s+(?P<aunit>second|minute|hour|day|week|month|year)"
    r"|(?P<num>\d+)\s+(?P<unit>seconds?|minutes?|hours?|days?|weeks?|months?|years?))",
    re.IGNORECASE,
)
_UNIT_TO_SECONDS: dict[str, int] = {
    "second": 1,
    "minute": 60,
    "hour": 3600,
    "day": 86400,
    "week": 604800,
    "month": 2592000,
    "year": 31536000,
}


def parse_container_health(status: str | None) -> ContainerHealth:
    """Extract the healthcheck value from a Docker status string."""
    if not status:
        return ContainerHealth.NONE
    match = _HEALTH_RE.search(status)
    if not match:
        return ContainerHealth.NONE
    value = match.group(1)
    if value == "health: starting":
        return ContainerHealth.STARTING
    return ContainerHealth(value)


def parse_container_uptime(status: str | None, now: datetime) -> datetime | None:
    """Compute the container start timestamp from a Docker status string."""
    if not status or not status.startswith("Up "):
        return None
    match = _UPTIME_NUMBER_RE.match(status)
    if not match:
        return None
    if match.group("lunit"):
        seconds = 0
    elif aunit := match.group("aunit"):
        seconds = _UNIT_TO_SECONDS[aunit.lower()]
    else:
        unit = match.group("unit").lower().rstrip("s")
        seconds = int(match.group("num")) * _UNIT_TO_SECONDS[unit]
    return now - timedelta(seconds=seconds)
