# [H] CVE-2017-9987

## Summary
Severity: High
Advisory: CVE-2017-9987
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9987
Type: osv

## Details
There is a heap-based buffer overflow in the function hpel_motion in mpegvideo_motion.c in libav 12.1. A crafted input can lead to a remote denial of service attack.

## References
- https://lists.debian.org/debian-lts-announce/2019/09/msg00000.html
- https://bugzilla.libav.org/show_bug.cgi?id=1067
