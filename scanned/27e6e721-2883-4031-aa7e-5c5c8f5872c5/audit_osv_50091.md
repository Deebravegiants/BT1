# [M] CVE-2019-8354

## Summary
Severity: Medium
Advisory: CVE-2019-8354
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-15
Source: https://osv.dev/vulnerability/CVE-2019-8354
Type: osv

## Details
An issue was discovered in SoX 14.4.2. lsx_make_lpf in effect_i_dsp.c has an integer overflow on the result of multiplication fed into malloc. When the buffer is allocated, it is smaller than expected, leading to a heap-based buffer overflow.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00040.html
- https://usn.ubuntu.com/4079-1/
- https://usn.ubuntu.com/4079-2/
- https://sourceforge.net/p/sox/bugs/319
