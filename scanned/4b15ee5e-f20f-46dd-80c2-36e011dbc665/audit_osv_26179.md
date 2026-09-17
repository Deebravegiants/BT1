# [H] CVE-2023-52425

## Summary
Severity: High
Advisory: CVE-2023-52425
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-04
Source: https://osv.dev/vulnerability/CVE-2023-52425
Type: osv

## Details
libexpat through 2.5.0 allows a denial of service (resource consumption) because many full reparsings are required in the case of a large token for which multiple buffer fills are needed.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PNRIHC7DVVRAIWFRGV23Y6UZXFBXSQDB/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52425.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PNRIHC7DVVRAIWFRGV23Y6UZXFBXSQDB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WNUBSGZFEZOBHJFTAD42SAN4ATW2VEMV/
- https://nvd.nist.gov/vuln/detail/CVE-2023-52425
- https://security.netapp.com/advisory/ntap-20240614-0003/
- https://github.com/libexpat/libexpat/pull/789
- http://www.openwall.com/lists/oss-security/2024/03/20/5
- https://lists.debian.org/debian-lts-announce/2024/04/msg00006.html
