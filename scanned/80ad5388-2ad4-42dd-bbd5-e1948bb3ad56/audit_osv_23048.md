# [M] CVE-2022-42706

## Summary
Severity: Medium
Advisory: CVE-2022-42706
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/CVE-2022-42706
Type: osv

## Details
An issue was discovered in Sangoma Asterisk through 16.28, 17 and 18 through 18.14, 19 through 19.6, and certified through 18.9-cert1. GetConfig, via Asterisk Manager Interface, allows a connected application to access files outside of the asterisk configuration directory, aka Directory Traversal.

## References
- https://downloads.asterisk.org/pub/security/AST-2022-009.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/42xxx/CVE-2022-42706.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-42706
- https://www.debian.org/security/2023/dsa-5358
- https://lists.debian.org/debian-lts-announce/2023/02/msg00029.html
