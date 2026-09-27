# [H] CVE-2017-6892

## Summary
Severity: High
Advisory: CVE-2017-6892
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-12
Source: https://osv.dev/vulnerability/CVE-2017-6892
Type: osv

## Details
In libsndfile version 1.0.28, an error in the "aiff_read_chanmap()" function (aiff.c) can be exploited to cause an out-of-bounds read memory access via a specially crafted AIFF file.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00030.html
- https://usn.ubuntu.com/4013-1/
- https://secuniaresearch.flexerasoftware.com/advisories/76717/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2017-13/
- https://security.gentoo.org/glsa/201811-23
- https://github.com/erikd/libsndfile/commit/f833c53cb596e9e1792949f762e0b33661822748
