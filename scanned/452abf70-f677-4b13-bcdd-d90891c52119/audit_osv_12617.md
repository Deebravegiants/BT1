# [M] CVE-2018-13419

## Summary
Severity: Medium
Advisory: CVE-2018-13419
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-07
Source: https://osv.dev/vulnerability/CVE-2018-13419
Type: osv

## Details
An issue has been found in libsndfile 1.0.28. There is a memory leak in psf_allocate in common.c, as demonstrated by sndfile-convert. NOTE: The maintainer and third parties were unable to reproduce and closed the issue

## References
- https://github.com/erikd/libsndfile/issues/398
