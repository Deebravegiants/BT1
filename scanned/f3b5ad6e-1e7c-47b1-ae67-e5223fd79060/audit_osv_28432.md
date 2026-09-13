# [H] FreeRDP rdp_write_logon_info_v1 NULL access

## Summary
Severity: High
Advisory: CVE-2024-32661
Aliases: GHSA-p5m5-342g-pv9m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-23
Source: https://osv.dev/vulnerability/CVE-2024-32661
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. FreeRDP based clients prior to version 3.5.1 are vulnerable to a possible `NULL` access and crash. Version 3.5.1 contains a patch for the issue. No known workarounds are available.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5JL476WVJSIE7SBUKVJRVA6A52V2HOLZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7SIS6NUNLUBOV4CPCSWKDE6T6C2W3WTR/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PX3U6YPZQ7PEJBVKSBUOLWVH7DHROHY5/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZKI4UISUXYNBPN4K6TIQKDRTIJ6CDCKJ/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32661.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-p5m5-342g-pv9m
- https://nvd.nist.gov/vuln/detail/CVE-2024-32661
- https://github.com/FreeRDP/FreeRDP/commit/71e463e31b4d69f4022d36bfc814592f56600793
