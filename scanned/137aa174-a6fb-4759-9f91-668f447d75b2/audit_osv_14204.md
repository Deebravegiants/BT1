# [M] CVE-2018-7875

## Summary
Severity: Medium
Advisory: CVE-2018-7875
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-08
Source: https://osv.dev/vulnerability/CVE-2018-7875
Type: osv

## Details
There is a heap-based buffer over-read in the getString function of util/decompile.c in libming 0.4.8 for CONSTANT8 data. A Crafted input will lead to a denial of service attack.

## References
- https://lists.debian.org/debian-lts-announce/2018/04/msg00008.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=892260
- https://github.com/libming/libming/issues/112
