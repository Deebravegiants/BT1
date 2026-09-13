# [C] CVE-2017-14122

## Summary
Severity: Critical
Advisory: CVE-2017-14122
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-09-03
Source: https://osv.dev/vulnerability/CVE-2017-14122
Type: osv

## Details
unrar 0.0.1 (aka unrar-free or unrar-gpl) suffers from a stack-based buffer over-read in unrarlib.c, related to ExtrFile and stricomp.

## References
- http://www.openwall.com/lists/oss-security/2017/08/20/1
- https://lists.debian.org/debian-lts-announce/2021/02/msg00026.html
- https://bugs.debian.org/874060
