# [M] CVE-2019-8355

## Summary
Severity: Medium
Advisory: CVE-2019-8355
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-15
Source: https://osv.dev/vulnerability/CVE-2019-8355
Type: osv

## Details
An issue was discovered in SoX 14.4.2. In xmalloc.h, there is an integer overflow on the result of multiplication fed into the lsx_valloc macro that wraps malloc. When the buffer is allocated, it is smaller than expected, leading to a heap-based buffer overflow in channels_start in remix.c.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00040.html
- https://usn.ubuntu.com/4079-1/
- https://usn.ubuntu.com/4079-2/
- https://sourceforge.net/p/sox/bugs/320
