# [M] PX4 Autopilot MAVLink FTP Session Validation Logic Error Allows Operations on Invalid File Descriptors

## Summary
Severity: Medium
Advisory: CVE-2026-32713
Aliases: GHSA-pp2c-jr5g-6f2m
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32713
Type: osv

## Details
PX4 autopilot is a flight control solution for drones. Prior to 1.17.0-rc2, A logic error in the PX4 Autopilot MAVLink FTP session validation uses incorrect boolean logic (&& instead of ||), allowing BurstReadFile and WriteFile operations to proceed with invalid sessions or closed file descriptors. This enables an unauthenticated attacker to put the FTP subsystem into an inconsistent state, trigger operations on invalid file descriptors, and bypass session isolation checks. This vulnerability is fixed in 1.17.0-rc2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32713.json
- https://github.com/PX4/PX4-Autopilot/security/advisories/GHSA-pp2c-jr5g-6f2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-32713
