"""巩义燃气数据协调器。"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GasApi
from .config_flow import CONF_OPENID, CONF_USER_NAME

_LOGGER = logging.getLogger(__name__)

DOMAIN = "gongyi_gas"
SCAN_INTERVAL = timedelta(minutes=30)


class GasCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self._api = GasApi(
            entry.data[CONF_OPENID],
            entry.data[CONF_USER_NAME],
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.hass.async_add_executor_job(self._api.fetch_all)
        except Exception as exc:
            raise UpdateFailed(str(exc)) from exc
