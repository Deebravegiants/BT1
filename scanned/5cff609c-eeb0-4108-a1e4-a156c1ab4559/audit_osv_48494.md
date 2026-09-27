# [M] CVE-2017-8372

## Summary
Severity: Medium
Advisory: CVE-2017-8372
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-8372
Type: osv

## Details
The mad_layer_III function in layer3.c in Underbit MAD libmad 0.15.1b, if NDEBUG is omitted, allows remote attackers to cause a denial of service (assertion failure and application exit) via a crafted audio file.

## References
- https://lists.debian.org/debian-lts-announce/2018/05/msg00011.html
- https://www.debian.org/security/2018/dsa-4192
- https://blogs.gentoo.org/ago/2017/04/30/libmad-assertion-failure-in-layer3-c/
