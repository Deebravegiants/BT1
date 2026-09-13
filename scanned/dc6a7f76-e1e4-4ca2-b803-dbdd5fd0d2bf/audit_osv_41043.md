# [M] Out-of-bounds read in the camera device enumerator server (rdpecam) via unterminated DeviceName / VirtualChannelName

## Summary
Severity: Medium
Advisory: CVE-2026-57157
Aliases: GHSA-47fr-jw86-c3fj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-57157
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.28.0, FreeRDP server implementations with the MS-RDPECAM camera device enumerator channel enabled scan attacker-supplied DeviceName and VirtualChannelName fields for a NUL terminator in channels/rdpecam/server/camera_device_enumerator_main.c and then dereference once past the scan bound, allowing a malicious RDP client to trigger a 1- to 2-byte out-of-bounds heap read. This issue is fixed in version 3.28.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.28.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57157.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-47fr-jw86-c3fj
- https://nvd.nist.gov/vuln/detail/CVE-2026-57157
- https://github.com/FreeRDP/FreeRDP/commit/02991e7b3cc0b9800b09030c0e9c80bab877d668
- https://github.com/FreeRDP/FreeRDP/commit/bd789a31cb794750dbe5e7c0e205981074cb681a
- https://github.com/FreeRDP/FreeRDP/pull/12930
- https://github.com/FreeRDP/FreeRDP/pull/12945
