"""Unraid Binary Sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import callback

from . import _LOGGER
from .const import CONF_DOCKER_MODE, CONF_DRIVES, DOCKER_MODE_OFF
from .entity import UnraidBaseEntity, UnraidEntityDescription

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import UnraidConfigEntry
    from .models import Disk, DockerContainer


class UnraidDiskBinarySensorEntityDescription(
    UnraidEntityDescription, BinarySensorEntityDescription, frozen_or_thawed=True
):
    """Description for Unraid Binary Sensor Entity."""

    value_fn: Callable[[Disk], bool]
    extra_values_fn: Callable[[Disk], dict[str, Any]] | None = None


class UnraidDockerBinarySensorEntityDescription(
    UnraidEntityDescription, BinarySensorEntityDescription, frozen_or_thawed=True
):
    """Description for Unraid Docker Binary Sensor Entity."""

    value_fn: Callable[[DockerContainer], bool | None]


DISK_BINARY_SENSOR_DESCRIPTIONS: tuple[UnraidDiskBinarySensorEntityDescription, ...] = (
    UnraidDiskBinarySensorEntityDescription(
        key="disk_spinning",
        device_class=BinarySensorDeviceClass.MOVING,
        value_fn=lambda disk: disk.is_spinning,
    ),
)

DOCKER_OPT_IN_BINARY_SENSOR_DESCRIPTIONS: tuple[UnraidDockerBinarySensorEntityDescription, ...] = (
    UnraidDockerBinarySensorEntityDescription(
        key="docker_update_available",
        device_class=BinarySensorDeviceClass.UPDATE,
        value_fn=lambda container: container.update_available,
    ),
    UnraidDockerBinarySensorEntityDescription(
        key="docker_orphaned",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda container: container.orphaned,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    UnraidDockerBinarySensorEntityDescription(
        key="docker_rebuild_ready",
        device_class=BinarySensorDeviceClass.UPDATE,
        value_fn=lambda container: container.rebuild_ready,
    ),
    UnraidDockerBinarySensorEntityDescription(
        key="docker_auto_start",
        value_fn=lambda container: container.auto_start,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    config_entry: UnraidConfigEntry,
    async_add_entites: AddEntitiesCallback,
) -> None:
    """Set up this integration using config entry."""

    @callback
    def add_disk_callback(disk: Disk) -> None:
        _LOGGER.debug("Binary Sensor: Adding new disk: %s", disk.name)
        entities = [
            UnraidDiskBinarySensorEntity(description, config_entry, disk.id)
            for description in DISK_BINARY_SENSOR_DESCRIPTIONS
            if description.min_version <= config_entry.runtime_data.coordinator.api_client.version
        ]
        async_add_entites(entities)

    @callback
    def add_container_callback(container_name: str) -> None:
        if (
            config_entry.runtime_data.coordinator.data["docker_containers"].get(container_name)
            is None
        ):
            return
        _LOGGER.debug("Binary Sensor: Adding new Docker container: %s", container_name)
        api_version = config_entry.runtime_data.coordinator.api_client.version
        entities = [
            UnraidDockerBinarySensor(description, config_entry, container_name)
            for description in DOCKER_OPT_IN_BINARY_SENSOR_DESCRIPTIONS
            if description.min_version <= api_version
        ]
        config_entry.runtime_data.containers[container_name]["entities"].extend(entities)
        async_add_entites(entities)

    if config_entry.options[CONF_DRIVES]:
        config_entry.runtime_data.coordinator.subscribe_disks(add_disk_callback)
    if config_entry.options.get(CONF_DOCKER_MODE, DOCKER_MODE_OFF) != DOCKER_MODE_OFF:
        config_entry.runtime_data.coordinator.subscribe_docker(add_container_callback)


class UnraidDockerBinarySensor(UnraidBaseEntity, BinarySensorEntity):
    """Binary Sensor for Docker containers."""

    entity_description: UnraidDockerBinarySensorEntityDescription

    def __init__(
        self,
        description: UnraidDockerBinarySensorEntityDescription,
        config_entry: UnraidConfigEntry,
        container_name: str,
    ) -> None:
        super().__init__(description, config_entry)
        self.container_name = container_name
        self._attr_unique_id = f"{config_entry.entry_id}-{description.key}-{self.container_name}"
        self._attr_device_info = config_entry.runtime_data.containers[container_name]["device_info"]

    @property
    def is_on(self) -> bool | None:
        try:
            return self.entity_description.value_fn(
                self.coordinator.data["docker_containers"][self.container_name]
            )
        except (KeyError, AttributeError):
            return None

    @property
    def available(self) -> bool:
        return (
            self.container_name in self.coordinator.data["docker_containers"]
            and self.coordinator.last_update_success
        )


class UnraidDiskBinarySensorEntity(UnraidBaseEntity, BinarySensorEntity):
    """Binary Sensor for Unraid Disks."""

    entity_description: UnraidDiskBinarySensorEntityDescription

    def __init__(
        self,
        description: UnraidDiskBinarySensorEntityDescription,
        config_entry: UnraidConfigEntry,
        disk_id: str,
    ) -> None:
        super().__init__(description, config_entry)
        self.disk_id = disk_id
        self._attr_unique_id = f"{config_entry.entry_id}-{description.key}-{self.disk_id}"
        self._attr_translation_placeholders = {
            "disk_name": self.coordinator.data["disks"][self.disk_id].name
        }

    @property
    def is_on(self) -> bool | None:
        try:
            return self.entity_description.value_fn(self.coordinator.data["disks"][self.disk_id])
        except (KeyError, AttributeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        try:
            if self.entity_description.extra_values_fn:
                return self.entity_description.extra_values_fn(
                    self.coordinator.data["disks"][self.disk_id]
                )
        except (KeyError, AttributeError):
            return None
        return None
