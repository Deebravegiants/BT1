# [M] PX4 Autopilot: Stack-based Buffer Overflow via Oversized Path Input in MAVLink Log Request Handling

## Summary
Severity: Medium
Advisory: CVE-2026-32743
Aliases: GHSA-97c4-68r9-96p5
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-32743
Type: osv

## Details
PX4 is an open-source autopilot stack for drones and unmanned vehicles. Versions 1.17.0-rc2 and below are vulnerable to Stack-based Buffer Overflow through the MavlinkLogHandler, and are triggered via MAVLink log request. The LogEntry.filepath buffer is 60 bytes, but the sscanf function parses paths from the log list file with no width specifier, allowing a path longer than 60 characters to overflow the buffer. An attacker with MAVLink link access can trigger this by first creating deeply nested directories via MAVLink FTP, then requesting the log list. The flight controller MAVLink task crashes, losing telemetry and command capability and causing DoS. This issue has been fixed in this commit: https://github.com/PX4/PX4-Autopilot/commit/616b25a280e229c24d5cf12a03dbf248df89c474.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32743.json
- https://github.com/PX4/PX4-Autopilot/security/advisories/GHSA-97c4-68r9-96p5
- https://nvd.nist.gov/vuln/detail/CVE-2026-32743
- https://github.com/PX4/PX4-Autopilot/commit/616b25a280e229c24d5cf12a03dbf248df89c474
