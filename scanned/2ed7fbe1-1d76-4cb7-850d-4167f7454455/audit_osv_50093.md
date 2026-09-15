# [M] CVE-2019-8356

## Summary
Severity: Medium
Advisory: CVE-2019-8356
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-15
Source: https://osv.dev/vulnerability/CVE-2019-8356
Type: osv

## Details
An issue was discovered in SoX 14.4.2. One of the arguments to bitrv2 in fft4g.c is not guarded, such that it can lead to write access outside of the statically declared array, aka a stack-based buffer overflow.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00040.html
- https://usn.ubuntu.com/4079-1/
- https://usn.ubuntu.com/4079-2/
- https://sourceforge.net/p/sox/bugs/321
