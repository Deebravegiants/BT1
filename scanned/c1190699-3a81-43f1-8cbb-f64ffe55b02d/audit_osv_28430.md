# [C] freerdp_image_copy out of bound read

## Summary
Severity: Critical
Advisory: CVE-2024-32659
Aliases: GHSA-8jgr-7r33-x87w
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-23
Source: https://osv.dev/vulnerability/CVE-2024-32659
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. FreeRDP based clients prior to version 3.5.1 are vulnerable to out-of-bounds read if `((nWidth == 0) and (nHeight == 0))`. Version 3.5.1 contains a patch for the issue. No known workarounds are available.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5JL476WVJSIE7SBUKVJRVA6A52V2HOLZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7SIS6NUNLUBOV4CPCSWKDE6T6C2W3WTR/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PX3U6YPZQ7PEJBVKSBUOLWVH7DHROHY5/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZKI4UISUXYNBPN4K6TIQKDRTIJ6CDCKJ/
- https://oss-fuzz.com/testcase-detail/6156779722440704
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32659.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-8jgr-7r33-x87w
- https://nvd.nist.gov/vuln/detail/CVE-2024-32659
- https://github.com/FreeRDP/FreeRDP/commit/6430945ce003a5e24d454d8566f54aae1b6b617b
