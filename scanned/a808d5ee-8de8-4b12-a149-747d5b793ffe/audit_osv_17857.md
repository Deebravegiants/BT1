# [H] CVE-2020-21041

## Summary
Severity: High
Advisory: CVE-2020-21041
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-24
Source: https://osv.dev/vulnerability/CVE-2020-21041
Type: osv

## Details
Buffer Overflow vulnerability exists in FFmpeg 4.1 via apng_do_inverse_blend in libavcodec/pngenc.c, which could let a remote malicious user cause a Denial of Service

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/7989
