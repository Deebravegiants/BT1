# [H] FreeRDP: Integer Overflow in `freerdp_image_copy_from_icon_data` Bypasses Bounds Check

## Summary
Severity: High
Advisory: CVE-2026-55648
Aliases: GHSA-5c5v-f78v-h2f6
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-55648
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.27.0, freerdp_image_copy_from_icon_data in libfreerdp/codec/color.c calculates nWidth multiplied by nHeight multiplied by FreeRDPGetBytesPerPixel(format) in 32-bit arithmetic. A malicious RDP server can send a RAIL TS_ICON_INFO update with dimensions such as 32768 by 32768 and 32 bits per pixel so the required-size calculation wraps, bypassing the cbBitsColor source bounds check before freerdp_image_copy_no_overlap reads attacker-controlled icon data. This affects RemoteApp clients using the vulnerable library path, while xfreerdp has a caller-side mitigation. This issue is fixed in version 3.27.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55648.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-5c5v-f78v-h2f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-55648
- https://github.com/FreeRDP/FreeRDP/commit/e4ae473da2926724d9b6329778797a3bdea79eb3
- https://github.com/FreeRDP/FreeRDP/pull/12877
