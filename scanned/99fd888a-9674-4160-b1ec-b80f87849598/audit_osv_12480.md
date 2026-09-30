# [M] CVE-2018-12459

## Summary
Severity: Medium
Advisory: CVE-2018-12459
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-06-15
Source: https://osv.dev/vulnerability/CVE-2018-12459
Type: osv

## Details
An inconsistent bits-per-sample value in the ff_mpeg4_decode_picture_header function in libavcodec/mpeg4videodec.c in FFmpeg 4.0 may trigger an assertion violation while converting a crafted AVI file to MPEG4, leading to a denial of service.

## References
- https://github.com/FFmpeg/FFmpeg/commit/2fc108f60f98cd00813418a8754a46476b404a3c
