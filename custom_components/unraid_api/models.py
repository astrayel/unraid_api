"""Models for Unraid GraphQl Api."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DiskStatus(StrEnum):  # noqa: D101
    DISK_NP = "DISK_NP"
    DISK_OK = "DISK_OK"
    DISK_NP_MISSING = "DISK_NP_MISSING"
    DISK_INVALID = "DISK_INVALID"
    DISK_WRONG = "DISK_WRONG"
    DISK_DSBL = "DISK_DSBL"
    DISK_NP_DSBL = "DISK_NP_DSBL"
    DISK_DSBL_NEW = "DISK_DSBL_NEW"
    DISK_NEW = "DISK_NEW"


class DiskType(StrEnum):  # noqa: D101
    Data = "DATA"
    Parity = "PARITY"
    Flash = "FLASH"
    Cache = "CACHE"


class DiskInterfaceType(StrEnum):  # noqa: D101
    SAS = "SAS"
    SATA = "SATA"
    USB = "USB"
    PCIE = "PCIE"
    NVME = "NVME"
    UNKNOWN = "UNKNOWN"


class DiskSmartStatus(StrEnum):  # noqa: D101
    OK = "OK"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class ArrayState(StrEnum):  # noqa: D101
    STARTED = "STARTED"
    STOPPED = "STOPPED"
    NEW_ARRAY = "NEW_ARRAY"
    RECON_DISK = "RECON_DISK"
    DISABLE_DISK = "DISABLE_DISK"
    SWAP_DSBL = "SWAP_DSBL"
    INVALID_EXPANSION = "INVALID_EXPANSION"
    PARITY_NOT_BIGGEST = "PARITY_NOT_BIGGEST"
    TOO_MANY_MISSING_DISKS = "TOO_MANY_MISSING_DISKS"
    NEW_DISK_TOO_SMALL = "NEW_DISK_TOO_SMALL"
    NO_DATA_DISKS = "NO_DATA_DISKS"


@dataclass
class ServerInfo:
    """Server Info."""

    localurl: str
    name: str
    unraid_version: str


@dataclass
class Metrics:
    """Metrics."""

    memory_free: int
    memory_total: int
    memory_active: int
    memory_available: int
    memory_percent_total: float
    cpu_percent_total: float


@dataclass
class Share:
    """Shares."""

    name: str
    free: int
    used: int
    size: int
    allocator: str
    floor: str


@dataclass
class Disk:
    """Disk."""

    name: str
    status: DiskStatus
    temp: int | None
    fs_size: int | None
    fs_free: int | None
    fs_used: int | None
    type: DiskType
    id: str
    is_spinning: bool
    # Extended info
    vendor: str | None = None
    model: str | None = None
    serial_num: str | None = None
    interface_type: DiskInterfaceType | None = None
    smart_status: DiskSmartStatus | None = None
    firmware_revision: str | None = None
    num_errors: int | None = None
    num_reads: int | None = None
    num_writes: int | None = None


@dataclass
class Array:
    """Array."""

    state: ArrayState
    capacity_free: int
    capacity_used: int
    capacity_total: int


class VmState(StrEnum):  # noqa: D101
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"
    PMSUSPENDED = "PMSUSPENDED"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    SHUTDOWN = "SHUTDOWN"
    CRASHED = "CRASHED"


class DockerState(StrEnum):  # noqa: D101
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"
    RESTARTING = "RESTARTING"
    CREATED = "CREATED"
    EXITED = "EXITED"
    DEAD = "DEAD"


@dataclass
class VirtualMachine:
    """Virtual Machine."""

    id: str
    name: str
    state: VmState


@dataclass
class DockerContainer:
    """Docker Container."""

    id: str
    name: str
    state: DockerState
    image: str
    autostart: bool


class ParityCheckStatus(StrEnum):  # noqa: D101
    NEVER_RUN = "NEVER_RUN"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


@dataclass
class ParityCheck:
    """Parity Check Status."""

    status: ParityCheckStatus
    progress: int | None  # 0-100
    errors: int | None
    speed: str | None  # Speed in MB/s
    duration: int | None  # Duration in seconds
    correcting: bool | None
    running: bool
    paused: bool


class UPSStatus(StrEnum):  # noqa: D101
    ONLINE = "ONLINE"
    ON_BATTERY = "ON_BATTERY"
    LOW_BATTERY = "LOW_BATTERY"
    REPLACE_BATTERY = "REPLACE_BATTERY"
    OVERLOAD = "OVERLOAD"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


@dataclass
class UPSDevice:
    """UPS Device."""

    id: str
    name: str
    model: str
    status: str  # Can be various statuses, keeping as string
    battery_level: int  # 0-100%
    runtime: int  # seconds
    battery_health: str  # "Good", "Replace", "Unknown"
    input_voltage: float
    output_voltage: float
    load_percentage: int  # 0-100%


class RegistrationType(StrEnum):  # noqa: D101
    BASIC = "BASIC"
    PLUS = "PLUS"
    PRO = "PRO"
    STARTER = "STARTER"
    UNLEASHED = "UNLEASHED"
    LIFETIME = "LIFETIME"
    INVALID = "INVALID"
    TRIAL = "TRIAL"


class RegistrationState(StrEnum):  # noqa: D101
    REGISTERED = "REGISTERED"
    UNREGISTERED = "UNREGISTERED"
    EXPIRED = "EXPIRED"
    BLACKLISTED = "BLACKLISTED"
    TRIAL = "TRIAL"


@dataclass
class Registration:
    """Server Registration/License."""

    id: str
    license_type: RegistrationType
    state: RegistrationState
    expiration: str | None  # Date string
    update_expiration: str | None  # Date string


@dataclass
class Flash:
    """USB Flash Drive."""

    id: str
    guid: str
    vendor: str
    product: str
