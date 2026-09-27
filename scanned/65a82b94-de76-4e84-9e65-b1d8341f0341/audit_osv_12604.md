# [M] CVE-2018-13301

## Summary
Severity: Medium
Advisory: CVE-2018-13301
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-13301
Type: osv

## Details
In FFmpeg 4.0.1, due to a missing check of a profile value before setting it, the ff_mpeg4_decode_picture_header function in libavcodec/mpeg4videodec.c may trigger a NULL pointer dereference while converting a crafted AVI file to MPEG4, leading to a denial of service.

## References
- http://www.securityfocus.com/bid/104675
- https://github.com/FFmpeg/FFmpeg/commit/2aa9047486dbff12d9e040f917e5f799ed2fd78b
