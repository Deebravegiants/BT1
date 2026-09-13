# [C] CVE-2021-20001

## Summary
Severity: Critical
Advisory: CVE-2021-20001
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-11
Source: https://osv.dev/vulnerability/CVE-2021-20001
Type: osv

## Details
It was discovered, that debian-edu-config, a set of configuration files used for the Debian Edu blend, before 2.12.16 configured insecure permissions for the user web shares (~/public_html), which could result in privilege escalation.

## References
- https://lists.debian.org/debian-lts-announce/2022/02/msg00012.html
- https://lists.debian.org/debian-security-announce/2022/msg00039.html
- https://www.debian.org/security/2022/dsa-5072
- https://salsa.debian.org/debian-edu/debian-edu-config/-/commit/4d39a5888d193567704238f8c035f8d17cfe34e5
