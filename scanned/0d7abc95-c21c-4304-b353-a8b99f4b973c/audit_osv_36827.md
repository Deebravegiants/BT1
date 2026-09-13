# [M] FreeRDP: vuln_1_15_1 RDPGFX WIRE_TO_SURFACE_2 Out-of-Bounds Read

## Summary
Severity: Medium
Advisory: CVE-2026-25941
Aliases: GHSA-3546-x645-5cf8
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25941
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Versions on the 2.x branch prior to to 2.11.8 and on the 3.x branch prior to 3.23.0 have an out-of-bounds read vulnerability in the FreeRDP client's RDPGFX channel that allows a malicious RDP server to read uninitialized heap memory by sending a crafted WIRE_TO_SURFACE_2 PDU with a `bitmapDataLength` value larger than the actual data in the packet. This can lead to information disclosure or client crashes when a user connects to a malicious server. Versions 2.11.8 and 3.23.0 fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25941.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-3546-x645-5cf8
- https://nvd.nist.gov/vuln/detail/CVE-2026-25941
- https://github.com/FreeRDP/FreeRDP/commit/2e3b77e28ac6a398897d28ba464dcc5dfab9c9e2
