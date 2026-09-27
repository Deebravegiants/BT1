# [M] CVE-2018-13304

## Summary
Severity: Medium
Advisory: CVE-2018-13304
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-13304
Type: osv

## Details
In libavcodec in FFmpeg 4.0.1, improper maintenance of the consistency between the context profile field and studio_profile in libavcodec may trigger an assertion failure while converting a crafted AVI file to MPEG4, leading to a denial of service, related to error_resilience.c, h263dec.c, and mpeg4videodec.c.

## References
- https://github.com/FFmpeg/FFmpeg/commit/bd27a9364ca274ca97f1df6d984e88a0700fb235
