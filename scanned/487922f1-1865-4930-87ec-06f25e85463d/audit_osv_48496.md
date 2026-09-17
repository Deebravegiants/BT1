# [M] CVE-2017-8374

## Summary
Severity: Medium
Advisory: CVE-2017-8374
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-8374
Type: osv

## Details
The mad_bit_skip function in bit.c in Underbit MAD libmad 0.15.1b allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted audio file.

## References
- https://lists.debian.org/debian-lts-announce/2018/05/msg00011.html
- https://www.debian.org/security/2018/dsa-4192
- https://blogs.gentoo.org/ago/2017/04/30/libmad-heap-based-buffer-overflow-in-mad_bit_skip-bit-c/
