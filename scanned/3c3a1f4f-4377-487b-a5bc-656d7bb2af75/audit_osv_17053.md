# [C] CVE-2020-11729

## Summary
Severity: Critical
Advisory: CVE-2020-11729
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/CVE-2020-11729
Type: osv

## Details
An issue was discovered in DAViCal Andrew's Web Libraries (AWL) through 0.60. Long-term session cookies, uses to provide long-term session continuity, are not generated securely, enabling a brute-force attack that may be successful.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=956650
- https://lists.debian.org/debian-lts-announce/2020/04/msg00011.html
- https://www.debian.org/security/2020/dsa-4660
- https://gitlab.com/davical-project/awl/-/issues/18
