# [H] CVE-2018-16743

## Summary
Severity: High
Advisory: CVE-2018-16743
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-13
Source: https://osv.dev/vulnerability/CVE-2018-16743
Type: osv

## Details
An issue was discovered in mgetty before 1.2.1. In contrib/next-login/login.c, the command-line parameter username is passed unsanitized to strcpy(), which can cause a stack-based buffer overflow.

## References
- https://www.x41-dsec.de/lab/advisories/x41-2018-007-mgetty
