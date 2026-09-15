# [H] FreeRDP zgfx_decompress out of memory vulnerability

## Summary
Severity: High
Advisory: CVE-2024-32660
Aliases: GHSA-mxv6-2cw6-m3mx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-23
Source: https://osv.dev/vulnerability/CVE-2024-32660
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.5.1, a malicious server can crash the FreeRDP client by sending invalid huge allocation size. Version 3.5.1 contains a patch for the issue. No known workarounds are available.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5JL476WVJSIE7SBUKVJRVA6A52V2HOLZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7SIS6NUNLUBOV4CPCSWKDE6T6C2W3WTR/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PX3U6YPZQ7PEJBVKSBUOLWVH7DHROHY5/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZKI4UISUXYNBPN4K6TIQKDRTIJ6CDCKJ/
- https://oss-fuzz.com/testcase-detail/5559242514825216
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32660.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-mxv6-2cw6-m3mx
- https://nvd.nist.gov/vuln/detail/CVE-2024-32660
- https://github.com/FreeRDP/FreeRDP/commit/5e5d27cf310e4c10b854be7667bfb7a5d774eb47
