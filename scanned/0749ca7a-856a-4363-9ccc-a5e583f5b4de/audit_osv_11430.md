# [M] CVE-2017-7741

## Summary
Severity: Medium
Advisory: CVE-2017-7741
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-7741
Type: osv

## Details
In libsndfile before 1.0.28, an error in the "flac_buffer_copy()" function (flac.c) can be exploited to cause a segmentation violation (with write memory access) via a specially crafted FLAC file during a resample attempt, a similar issue to CVE-2017-7585.

## References
- https://security.gentoo.org/glsa/201707-04
- https://blogs.gentoo.org/ago/2017/04/11/libsndfile-invalid-memory-read-and-invalid-memory-write-in/
- https://github.com/erikd/libsndfile/commit/60b234301adf258786d8b90be5c1d437fc8799e0
