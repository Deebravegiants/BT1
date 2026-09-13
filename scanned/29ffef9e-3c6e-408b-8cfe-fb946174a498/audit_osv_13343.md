# [M] CVE-2018-19432

## Summary
Severity: Medium
Advisory: CVE-2018-19432
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-22
Source: https://osv.dev/vulnerability/CVE-2018-19432
Type: osv

## Details
An issue was discovered in libsndfile 1.0.28. There is a NULL pointer dereference in the function sf_write_int in sndfile.c, which will lead to a denial of service.

## References
- https://usn.ubuntu.com/4013-1/
- http://www.securityfocus.com/bid/105996
- https://lists.debian.org/debian-lts-announce/2018/12/msg00016.html
- https://github.com/erikd/libsndfile/issues/427
