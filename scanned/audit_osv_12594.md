# [H] CVE-2018-13139

## Summary
Severity: High
Advisory: CVE-2018-13139
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-04
Source: https://osv.dev/vulnerability/CVE-2018-13139
Type: osv

## Details
A stack-based buffer overflow in psf_memset in common.c in libsndfile 1.0.28 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted audio file. The vulnerability can be triggered by the executable sndfile-deinterleave.

## References
- https://usn.ubuntu.com/4013-1/
- https://lists.debian.org/debian-lts-announce/2018/12/msg00016.html
- https://security.gentoo.org/glsa/201811-23
- https://github.com/erikd/libsndfile/issues/397
