# [M] CVE-2018-5747

## Summary
Severity: Medium
Advisory: CVE-2018-5747
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-17
Source: https://osv.dev/vulnerability/CVE-2018-5747
Type: osv

## Details
In Long Range Zip (aka lrzip) 0.631, there is a use-after-free in the ucompthread function (stream.c). Remote attackers could leverage this vulnerability to cause a denial of service via a crafted lrz file.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00001.html
- https://github.com/ckolivas/lrzip/issues/90
