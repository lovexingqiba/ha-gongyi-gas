"""巩义燃气传感器实体。"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import GasCoordinator
from .config_flow import CONF_DEVICE_NAME

DOMAIN = "gongyi_gas"

SENSOR_DEFINITIONS: list[dict[str, Any]] = [
    {
        "key": "balance",
        "name": "燃气余额",
        "device_class": SensorDeviceClass.MONETARY,
        "unit": "CNY",
        "icon": "mdi:fire",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "yesterday_usage",
        "name": "昨日用气量",
        "device_class": SensorDeviceClass.GAS,
        "unit": UnitOfVolume.CUBIC_METERS,
        "icon": "mdi:meter-gas",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "yesterday_fee",
        "name": "昨日燃气费",
        "device_class": SensorDeviceClass.MONETARY,
        "unit": "CNY",
        "icon": "mdi:cash",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "update_time",
        "name": "更新时间",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "unit": None,
        "icon": "mdi:clock-outline",
        "state_class": None,
    },
    {
        "key": "meter_number",
        "name": "燃气表号",
        "device_class": None,
        "unit": None,
        "icon": "mdi:counter",
        "state_class": None,
    },
    {
        "key": "address",
        "name": "地址",
        "device_class": None,
        "unit": None,
        "icon": "mdi:map-marker",
        "state_class": None,
    },
]


def _to_iso(dt_str: str) -> str:
    """转为 ISO 8601 格式。"""
    dt_str = dt_str.strip()
    if not dt_str:
        return ""
    dt_str = dt_str.replace(" ", "T")
    if "T" not in dt_str or dt_str.count(":") == 0:
        dt_str = dt_str.split("T")[0] + "T00:00:00" if "T" in dt_str else dt_str + "T00:00:00"
    elif dt_str.count(":") == 1:
        dt_str += ":00"
    if "+" not in dt_str and "Z" not in dt_str:
        dt_str += "+08:00"
    return dt_str


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: GasCoordinator = entry.runtime_data
    async_add_entities(
        GasSensor(coordinator, definition, entry) for definition in SENSOR_DEFINITIONS
    )


class GasSensor(CoordinatorEntity[GasCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GasCoordinator,
        definition: dict[str, Any],
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._key = definition["key"]
        self._attr_unique_id = f"{DOMAIN}_{self._key}"
        self._attr_translation_key = self._key
        self._attr_device_class = definition["device_class"]
        self._attr_native_unit_of_measurement = definition["unit"]
        self._attr_icon = definition["icon"]
        self._attr_state_class = definition["state_class"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_DEVICE_NAME, "乐和园燃气"),
            manufacturer="巩义市燃气有限公司",
            model="物联网表",
            sw_version="1.0.0",
        )

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self._key)
        if value is None:
            return None
        if self._attr_device_class is SensorDeviceClass.TIMESTAMP and isinstance(value, str):
            try:
                return datetime.fromisoformat(_to_iso(value))
            except (ValueError, TypeError):
                pass
        # 数值类型转换
        if isinstance(value, (int, float)):
            return value
        return value
