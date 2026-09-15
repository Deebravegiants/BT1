# [M] CVE-2017-14634

## Summary
Severity: Medium
Advisory: CVE-2017-14634
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14634
Type: osv

## Details
In libsndfile 1.0.28, a divide-by-zero error exists in the function double64_init() in double64.c, which may lead to DoS when playing a crafted audio file.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00030.html
- https://usn.ubuntu.com/4013-1/
- https://github.com/erikd/libsndfile/issues/318
- https://security.gentoo.org/glsa/201811-23
- https://lists.debian.org/debian-lts-announce/2018/12/msg00016.html
