# [H] CVE-2018-7871

## Summary
Severity: High
Advisory: CVE-2018-7871
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-08
Source: https://osv.dev/vulnerability/CVE-2018-7871
Type: osv

## Details
There is a heap-based buffer over-read in the getName function of util/decompile.c in libming 0.4.8 for CONSTANT16 data. A crafted input will lead to a denial of service or possibly unspecified other impact.

## References
- https://lists.debian.org/debian-lts-announce/2018/04/msg00008.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=892260
- https://github.com/libming/libming/issues/120
