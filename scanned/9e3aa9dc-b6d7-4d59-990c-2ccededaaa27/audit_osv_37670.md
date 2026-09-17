# [M] PX4 autopilot BST Device Name Length Can Overflow Driver Buffer

## Summary
Severity: Medium
Advisory: CVE-2026-32705
Aliases: GHSA-79mp-34pp-2f3f
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32705
Type: osv

## Details
PX4 autopilot is a flight control solution for drones. Prior to 1.17.0-rc2, the BST telemetry probe writes a string terminator using a device-provided length without bounds. A malicious BST device can report an oversized dev_name_len, causing a stack overflow in the driver and crashing the task (or enabling code execution). This vulnerability is fixed in 1.17.0-rc2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32705.json
- https://github.com/PX4/PX4-Autopilot/security/advisories/GHSA-79mp-34pp-2f3f
- https://nvd.nist.gov/vuln/detail/CVE-2026-32705
