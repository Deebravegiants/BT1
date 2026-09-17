# [M] Meeting Room Booking System has server-side request forgery in import functionality

## Summary
Severity: Medium
Advisory: CVE-2026-46382
Aliases: GHSA-gh77-mpcm-f8r3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-46382
Type: osv

## Details
The Meeting Room Booking System (MRBS) is a PHP-based application for booking meeting rooms. Prior to version 1.12.2, a user-supplied private/local URI can be made to be fetched without checks. Version 1.12.2 contains a fix. No known workarounds are available.

## References
- https://github.com/meeting-room-booking-system/mrbs-code/releases/tag/v1.12.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46382.json
- https://github.com/meeting-room-booking-system/mrbs-code/security/advisories/GHSA-gh77-mpcm-f8r3
- https://nvd.nist.gov/vuln/detail/CVE-2026-46382
