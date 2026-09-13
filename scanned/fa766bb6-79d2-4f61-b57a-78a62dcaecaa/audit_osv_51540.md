# [M] CVE-2021-32280

## Summary
Severity: Medium
Advisory: CVE-2021-32280
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32280
Type: osv

## Details
An issue was discovered in fig2dev before 3.2.8.. A NULL pointer dereference exists in the function compute_closed_spline() located in trans_spline.c. It allows an attacker to cause Denial of Service. The fixed version of fig2dev is 3.2.8.

## References
- https://lists.debian.org/debian-lts-announce/2021/10/msg00002.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00044.html
- https://sourceforge.net/p/mcj/fig2dev/ci/f17a3b8a7d54c1bc56ab92512531772a0b3ec991/
- https://sourceforge.net/p/mcj/tickets/107/
