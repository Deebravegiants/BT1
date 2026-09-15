# [H] CVE-2021-33815

## Summary
Severity: High
Advisory: CVE-2021-33815
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-03
Source: https://osv.dev/vulnerability/CVE-2021-33815
Type: osv

## Details
dwa_uncompress in libavcodec/exr.c in FFmpeg 4.4 allows an out-of-bounds array access because dc_count is not strictly checked.

## References
- https://security.gentoo.org/glsa/202312-14
- https://github.com/FFmpeg/FFmpeg/commit/26d3c81bc5ef2f8c3f09d45eaeacfb4b1139a777
