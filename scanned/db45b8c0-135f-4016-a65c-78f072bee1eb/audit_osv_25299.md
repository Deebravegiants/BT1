# [M] CVE-2023-33460

## Summary
Severity: Medium
Advisory: CVE-2023-33460
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-06
Source: https://osv.dev/vulnerability/CVE-2023-33460
Type: osv

## Details
There's a memory leak in yajl 2.1.0 with use of yajl_tree_parse function. which will cause out-of-memory in server and cause crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33460.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IBUUHG27RM4ROEYKMVRROR27AX6R63MB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KLE3C4CECEJ4EUYI56KXI6OWACWXX7WN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YO32YDJ74DADC7CMJNLSLBVWN5EXGF5J/
- https://nvd.nist.gov/vuln/detail/CVE-2023-33460
- https://github.com/lloyd/yajl/issues/250
- https://lists.debian.org/debian-lts-announce/2023/07/msg00000.html
- https://lists.debian.org/debian-lts-announce/2023/07/msg00013.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00003.html
