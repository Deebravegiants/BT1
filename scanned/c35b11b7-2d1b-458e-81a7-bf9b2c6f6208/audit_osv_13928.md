# [M] CVE-2018-5650

## Summary
Severity: Medium
Advisory: CVE-2018-5650
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-12
Source: https://osv.dev/vulnerability/CVE-2018-5650
Type: osv

## Details
In Long Range Zip (aka lrzip) 0.631, there is an infinite loop and application hang in the unzip_match function in runzip.c. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted lrz file.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00001.html
- https://github.com/ckolivas/lrzip/issues/88
