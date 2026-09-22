# [M] CVE-2018-19542

## Summary
Severity: Medium
Advisory: CVE-2018-19542
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-26
Source: https://osv.dev/vulnerability/CVE-2018-19542
Type: osv

## Details
An issue was discovered in JasPer 2.0.14. There is a NULL pointer dereference in the function jp2_decode in libjasper/jp2/jp2_dec.c, leading to a denial of service.

## References
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00004.html
- https://lists.debian.org/debian-lts-announce/2019/01/msg00003.html
- https://github.com/mdadams/jasper/issues/182
