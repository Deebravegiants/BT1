# [M] CVE-2020-25269

## Summary
Severity: Medium
Advisory: CVE-2020-25269
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/CVE-2020-25269
Type: osv

## Details
An issue was discovered in InspIRCd 2 before 2.0.29 and 3 before 3.6.0. The pgsql module contains a use after free vulnerability. When combined with the sqlauth or sqloper modules, this vulnerability can be used for remote crashing of an InspIRCd server by any user able to connect to a server.

## References
- https://docs.inspircd.org/security/2020-01/
- https://lists.debian.org/debian-lts-announce/2020/09/msg00015.html
- https://www.debian.org/security/2020/dsa-4764
- https://github.com/inspircd/inspircd/compare/426d1c8...b3f1db9
- https://github.com/inspircd/inspircd/compare/v2.0.28...07d7dea
