# [M] CVE-2018-19128

## Summary
Severity: Medium
Advisory: CVE-2018-19128
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-09
Source: https://osv.dev/vulnerability/CVE-2018-19128
Type: osv

## Details
In Libav 12.3, there is a heap-based buffer over-read in decode_frame in libavcodec/lcldec.c that allows an attacker to cause denial-of-service via a crafted avi file.

## References
- https://lists.debian.org/debian-lts-announce/2019/12/msg00003.html
- https://bugzilla.libav.org/show_bug.cgi?id=1137
