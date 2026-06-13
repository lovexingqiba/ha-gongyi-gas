"""巩义燃气配置流。"""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .api import GasApi

_LOGGER = logging.getLogger(__name__)

DOMAIN = "gongyi_gas"
CONF_OPENID = "openid"
CONF_USER_NAME = "user_name"
CONF_DEVICE_NAME = "device_name"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_OPENID): str,
        vol.Required(CONF_USER_NAME): str,
        vol.Optional(CONF_DEVICE_NAME, default="乐和园燃气"): str,
    }
)


class GasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                api = GasApi(
                    user_input[CONF_OPENID],
                    user_input[CONF_USER_NAME],
                )
                await self.hass.async_add_executor_job(api.fetch_all)
            except Exception as exc:
                _LOGGER.exception("查询失败: %s", exc)
                errors["base"] = "cannot_connect"
            else:
                device_name = user_input.get(CONF_DEVICE_NAME, "乐和园燃气")
                await self.async_set_unique_id(
                    f"gongyi_gas_{user_input[CONF_OPENID]}_{user_input[CONF_USER_NAME]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=device_name,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
