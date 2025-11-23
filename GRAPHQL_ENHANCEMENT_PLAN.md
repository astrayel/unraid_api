# Unraid Integration - GraphQL Enhancement Plan

## Executive Summary

Based on the complete Unraid GraphQL schema analysis, this document outlines the enhancement plan to add missing features to the Home Assistant Unraid integration.

## Current Implementation Status

### ✅ Already Implemented
- **Array Monitoring**: State, capacity (free/used/total)
- **Disk Monitoring**: Status, temperature, space usage, spinning status
- **Share Monitoring**: Free space with allocator details
- **System Metrics**: CPU utilization, RAM usage
- **VM Management**: State monitoring, power control, reboot/pause/resume
- **Docker Management**: Container state, start/stop control
- **Aggregate Counters**: VM and Docker counts by state

### 📊 Available in GraphQL but NOT Implemented

## Priority 1: High-Value Additions

### 1. Parity Check Monitoring 🔴 HIGH PRIORITY

**GraphQL Type**: `ParityCheck`

**Available Fields**:
```graphql
type ParityCheck {
  date: DateTime
  duration: Int          # Duration in seconds
  speed: String         # Speed in MB/s
  status: ParityCheckStatus!  # NEVER_RUN, RUNNING, PAUSED, COMPLETED, CANCELLED, FAILED
  errors: Int
  progress: Int         # Percentage 0-100
  correcting: Boolean
  paused: Boolean
  running: Boolean
}
```

**Query**: `parityHistory: [ParityCheck!]!` and `array.parityCheckStatus: ParityCheck!`

**Proposed Entities**:
- **Sensor** `parity_check_status` - Enum sensor (NEVER_RUN, RUNNING, PAUSED, COMPLETED, etc.)
- **Sensor** `parity_check_progress` - Percentage (0-100)
- **Sensor** `parity_check_errors` - Count of errors
- **Sensor** `parity_check_speed` - Speed in MB/s (as attribute)
- **Binary Sensor** `parity_check_running` - True when running
- **Extra Attributes**: duration, date, correcting status

**Benefits**: Critical for monitoring array health and catching disk failures early

---

### 2. UPS Monitoring 🔴 HIGH PRIORITY

**GraphQL Type**: `UPSDevice`

**Available Fields**:
```graphql
type UPSDevice {
  id: ID!
  name: String!
  model: String!
  status: String!        # "Online", "On Battery", "Low Battery", etc.
  battery: UPSBattery! {
    chargeLevel: Int!    # 0-100%
    estimatedRuntime: Int!  # seconds
    health: String!      # "Good", "Replace", "Unknown"
  }
  power: UPSPower! {
    inputVoltage: Float!
    outputVoltage: Float!
    loadPercentage: Int!  # 0-100%
  }
}
```

**Query**: `upsDevices: [UPSDevice!]!`

**Proposed Entities**:
- **Sensor** `ups_battery_level` - Percentage with battery icon
- **Sensor** `ups_runtime` - Time remaining (converted to minutes/hours)
- **Sensor** `ups_status` - Enum sensor (Online, On Battery, Low Battery, etc.)
- **Sensor** `ups_load` - Percentage
- **Sensor** `ups_input_voltage` - Voltage
- **Sensor** `ups_output_voltage` - Voltage
- **Binary Sensor** `ups_on_battery` - True when on battery power
- **Binary Sensor** `ups_battery_low` - True when battery is low
- **Extra Attributes**: model, battery health

**Benefits**: Critical for power management and automatic shutdown scenarios

---

### 3. Extended Disk Information 🟡 MEDIUM PRIORITY

**GraphQL Type**: `Disk` (separate from `ArrayDisk`)

**Available Fields NOT Currently Used**:
```graphql
type Disk {
  device: String!           # /dev/sdb
  type: String!             # SSD, HDD
  name: String!             # Model name
  vendor: String!           # Manufacturer
  size: Float!              # Total size in bytes
  firmwareRevision: String!
  serialNum: String!
  interfaceType: DiskInterfaceType!  # SAS, SATA, USB, PCIE
  smartStatus: DiskSmartStatus!      # OK, UNKNOWN
  temperature: Float
  isSpinning: Boolean!
  partitions: [DiskPartition!]!
}
```

**Current Implementation Gap**: We query `ArrayDisk` but not the detailed `Disk` type

**Proposed Enhancements**:
- **Sensor** `disk_smart_status` - Enum sensor (OK, UNKNOWN)
- **Add to Attributes**: vendor, model, serial number, interface type, firmware version
- **Sensor** `disk_read_errors` - From ArrayDisk.numErrors (already available!)
- **Sensor** `disk_read_count` - From ArrayDisk.numReads
- **Sensor** `disk_write_count` - From ArrayDisk.numWrites

**Benefits**: Better disk health monitoring and SMART status visibility

---

## Priority 2: Useful Additions

### 4. Server Registration/License Monitoring 🟡 MEDIUM PRIORITY

**GraphQL Type**: `Registration`

**Available Fields**:
```graphql
type Registration {
  id: PrefixedID!
  type: registrationType   # BASIC, PLUS, PRO, TRIAL, etc.
  state: RegistrationState
  expiration: String
  updateExpiration: String
}

enum registrationType {
  BASIC, PLUS, PRO, STARTER, UNLEASHED, LIFETIME, INVALID, TRIAL
}
```

**Query**: `registration: Registration`

**Proposed Entities**:
- **Sensor** `license_type` - Enum sensor showing license level
- **Sensor** `license_state` - State sensor
- **Sensor** `license_expiration` - Date sensor (if applicable)
- **Binary Sensor** `license_valid` - True if registration is valid

**Benefits**: Monitor license status and renewal dates

---

### 5. Flash Drive Monitoring 🟢 LOW PRIORITY

**GraphQL Type**: `Flash`

**Available Fields**:
```graphql
type Flash {
  id: PrefixedID!
  guid: String!
  vendor: String!
  product: String!
}
```

**Query**: `flash: Flash!`

**Proposed Implementation**:
- Add flash drive info to device_info or as diagnostic sensors
- **Sensor** `flash_vendor` - Diagnostic sensor
- **Sensor** `flash_product` - Diagnostic sensor

**Benefits**: Identify flash drive for troubleshooting

---

### 6. Network Access URLs 🟢 LOW PRIORITY

**GraphQL Type**: `AccessUrl`

**Available Fields**:
```graphql
type AccessUrl {
  type: URL_TYPE!  # LAN, WIREGUARD, WAN, MDNS, OTHER
  name: String
  ipv4: URL
  ipv6: URL
}
```

**Query**: `network.accessUrls: [AccessUrl!]`

**Proposed Implementation**:
- Add access URLs as diagnostic attributes on the main device
- Could be useful for displaying connection options in UI

**Benefits**: Quick access to various connection methods

---

### 7. Per-Core CPU Utilization 🟢 LOW PRIORITY

**GraphQL Type**: `CpuUtilization`

**Available Fields NOT Currently Used**:
```graphql
type CpuUtilization {
  percentTotal: Float!     # ✅ Already implemented
  cpus: [CpuLoad!]!        # ❌ NOT implemented - per-core data
}

type CpuLoad {
  percentTotal: Float!
  percentUser: Float!
  percentSystem: Float!
  percentIdle: Float!
  # ... more detailed breakdowns
}
```

**Proposed Implementation**:
- **Optional**: Add per-core CPU sensors (disabled by default)
- Or add per-core data to extra_state_attributes of main CPU sensor

**Benefits**: Detailed CPU monitoring for performance troubleshooting

---

## Priority 3: Advanced Features

### 8. Parity Check Control (Mutations)

**GraphQL Mutations**:
```graphql
type ParityCheckMutations {
  start(correct: Boolean!): JSON!
  pause: JSON!
  resume: JSON!
  cancel: JSON!
}
```

**Proposed Implementation**:
- **Button** `parity_check_start` - Start parity check
- **Button** `parity_check_pause` - Pause parity check
- **Button** `parity_check_resume` - Resume parity check
- **Button** `parity_check_cancel` - Cancel parity check

**Benefits**: Control parity checks from Home Assistant

---

### 9. Array Control (Mutations)

**GraphQL Mutations**:
```graphql
type ArrayMutations {
  setState(input: ArrayStateInput!): UnraidArray!
  # START or STOP array
}
```

**Proposed Implementation**:
- **Switch** `array_power` - Start/stop the array
- **Very sensitive** - needs confirmation/safeguards

**Benefits**: Remote array management

---

### 10. Notification Integration

**GraphQL Type**: `Notification`

**Available Fields**:
```graphql
type Notification {
  title: String!
  subject: String!
  description: String!
  importance: NotificationImportance!  # ALERT, INFO, WARNING
  timestamp: String
}
```

**Query**: `notifications.list(filter: NotificationFilter!): [Notification!]!`

**Proposed Implementation**:
- Create Home Assistant events from Unraid notifications
- Or persistent notifications in HA UI
- Filter by importance level

**Benefits**: See Unraid alerts in Home Assistant

---

## Implementation Phases

### Phase 1: Critical Monitoring (Week 1)
1. ✅ Parity Check sensors
2. ✅ UPS monitoring
3. ✅ Extended disk information

### Phase 2: Additional Sensors (Week 2)
4. ✅ Registration/license sensors
5. ✅ Flash drive info
6. ✅ Network URLs

### Phase 3: Advanced Features (Week 3)
7. ✅ Per-core CPU (optional)
8. ✅ Parity check control buttons
9. ✅ Array control (with safeguards)

### Phase 4: Integration Features (Future)
10. ✅ Notification system
11. ✅ Event subscriptions (GraphQL subscriptions)

---

## Technical Considerations

### Error Handling
- All new queries should have graceful error handling
- UPS queries should not fail if no UPS is configured
- Parity check queries should handle "never run" state

### Configuration Options
- Add new config options for:
  - `CONF_UPS` - Enable UPS monitoring
  - `CONF_PARITY` - Enable parity check monitoring
  - `CONF_DETAILED_DISKS` - Enable detailed disk sensors
  - `CONF_NOTIFICATIONS` - Enable Unraid notification integration

### Performance
- Current update interval: 1 minute
- Consider separate update intervals for different data types:
  - Fast (30s): UPS battery, parity check progress
  - Normal (1m): Disks, array, VMs, Docker
  - Slow (5m): License info, flash info, system info

### Backward Compatibility
- All new features should be opt-in via configuration
- Existing entities should not change behavior
- Maintain current defaults (drives=True, shares=True, vms=False, docker=False)

---

## GraphQL Query Changes Required

### New Queries to Add:

1. **PARITY_CHECK_QUERY**
```graphql
query ParityCheck {
  array {
    parityCheckStatus {
      status
      progress
      errors
      speed
      duration
      date
      correcting
      paused
      running
    }
  }
}
```

2. **UPS_QUERY**
```graphql
query UPS {
  upsDevices {
    id
    name
    model
    status
    battery {
      chargeLevel
      estimatedRuntime
      health
    }
    power {
      inputVoltage
      outputVoltage
      loadPercentage
    }
  }
}
```

3. **REGISTRATION_QUERY**
```graphql
query Registration {
  registration {
    id
    type
    state
    expiration
    updateExpiration
  }
}
```

4. **FLASH_QUERY**
```graphql
query Flash {
  flash {
    id
    guid
    vendor
    product
  }
}
```

5. **EXTENDED_DISKS_QUERY**
```graphql
query DetailedDisks {
  disks {
    id
    device
    type
    name
    vendor
    size
    firmwareRevision
    serialNum
    interfaceType
    smartStatus
    temperature
    isSpinning
  }
}
```

---

## Success Metrics

- ✅ Zero breaking changes to existing functionality
- ✅ All new features opt-in via configuration
- ✅ Graceful degradation if features not available
- ✅ Comprehensive error logging
- ✅ Full translation support
- ✅ Documentation updated

---

## Notes

- Priority is based on user value and implementation complexity
- All features should follow existing patterns in the codebase
- GraphQL schema version: Based on Unraid API 7.2+
- Requires testing on actual Unraid server with UPS and parity checks configured
