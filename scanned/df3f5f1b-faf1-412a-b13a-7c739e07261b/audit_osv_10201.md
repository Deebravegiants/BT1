# [H] CVE-2017-14246

## Summary
Severity: High
Advisory: CVE-2017-14246
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14246
Type: osv

## Details
An out of bounds read in the function d2ulaw_array() in ulaw.c of libsndfile 1.0.28 may lead to a remote DoS attack or information disclosure, related to mishandling of the NAN and INFINITY floating-point values.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00030.html
- https://usn.ubuntu.com/4013-1/
- https://lists.debian.org/debian-lts-announce/2018/12/msg00016.html
- https://security.gentoo.org/glsa/202007-65
- https://github.com/erikd/libsndfile/issues/317
