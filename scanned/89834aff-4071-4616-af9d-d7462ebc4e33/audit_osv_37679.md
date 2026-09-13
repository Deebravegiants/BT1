# [M] PX4 autopilot has a heap Use-After-Free in MavlinkShell::available() via SERIAL_CONTROL Race Condition

## Summary
Severity: Medium
Advisory: CVE-2026-32724
Aliases: GHSA-j5w2-w79c-mqrw
CVSS: 5.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32724
Type: osv

## Details
PX4 autopilot is a flight control solution for drones. Prior to 1.17.0-rc1, a heap-use-after-free is detected in the MavlinkShell::available() function. The issue is caused by a race condition between the MAVLink receiver thread (which handles shell creation/destruction) and the telemetry sender thread (which polls the shell for available output). The issue is remotely triggerable via MAVLink SERIAL_CONTROL messages (ID 126), which can be sent by an external ground station or automated script. This vulnerability is fixed in 1.17.0-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32724.json
- https://github.com/PX4/PX4-Autopilot/security/advisories/GHSA-j5w2-w79c-mqrw
- https://nvd.nist.gov/vuln/detail/CVE-2026-32724
