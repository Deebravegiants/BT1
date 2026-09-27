# [M] CVE-2018-14395

## Summary
Severity: Medium
Advisory: CVE-2018-14395
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-19
Source: https://osv.dev/vulnerability/CVE-2018-14395
Type: osv

## Details
libavformat/movenc.c in FFmpeg 3.2 and 4.0.2 allows attackers to cause a denial of service (application crash caused by a divide-by-zero error) with a user crafted audio file when converting to the MOV audio format.

## References
- http://www.securitytracker.com/id/1041394
- https://www.debian.org/security/2018/dsa-4258
- https://github.com/FFmpeg/FFmpeg/commit/2c0e98a0b478284bdff6d7a4062522605a8beae5
- https://github.com/FFmpeg/FFmpeg/commit/fa19fbcf712a6a6cc5a5cfdc3254a97b9bce6582
