# [M] Microsoft UFO: Missing Authorization in DEVICE_INFO_REQUEST Allows a DEVICE Client to Read Another Device's system_info

## Summary
Severity: Medium
Advisory: CVE-2026-54568
Aliases: GHSA-hc27-j4p9-qm2x
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-54568
Type: osv

## Details
Microsoft UFO open-source framework for intelligent automation across devices and platforms. From 3.0.0 until 3.0.6, a client connected to the UFO WebSocket server as a DEVICE could call DEVICE_INFO_REQUEST with another device's target_id and receive that device's server-side system_info through ufo/server/ws/handler.py, because handle_device_info_request and get_device_info did not enforce the constellation-only role or object-level authorization boundary. This issue is fixed in version 3.0.6.

## References
- https://github.com/microsoft/UFO/releases/tag/3.0.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54568.json
- https://github.com/microsoft/UFO/security/advisories/GHSA-hc27-j4p9-qm2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-54568
- https://github.com/microsoft/UFO/commit/2558da4e7dd05096aa6b489eca64efed96126713
