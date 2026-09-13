# [M] CVE-2019-13590

## Summary
Severity: Medium
Advisory: CVE-2019-13590
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-14
Source: https://osv.dev/vulnerability/CVE-2019-13590
Type: osv

## Details
An issue was discovered in libsox.a in SoX 14.4.2. In sox-fmt.h (startread function), there is an integer overflow on the result of integer addition (wraparound to 0) fed into the lsx_calloc macro that wraps malloc. When a NULL pointer is returned, it is used without a prior check that it is a valid pointer, leading to a NULL pointer dereference on lsx_readbuf in formats_i.c.

## References
- https://lists.debian.org/debian-lts-announce/2023/02/msg00009.html
- https://sourceforge.net/p/sox/bugs/325/
