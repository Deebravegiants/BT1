# [M] CVE-2018-19661

## Summary
Severity: Medium
Advisory: CVE-2018-19661
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-19661
Type: osv

## Details
An issue was discovered in libsndfile 1.0.28. There is a buffer over-read in the function i2ulaw_array in ulaw.c that will lead to a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00030.html
- https://usn.ubuntu.com/4013-1/
- https://lists.debian.org/debian-lts-announce/2018/12/msg00016.html
- https://github.com/erikd/libsndfile/issues/429
