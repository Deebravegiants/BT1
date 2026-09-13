# [H] CVE-2020-22015

## Summary
Severity: High
Advisory: CVE-2020-22015
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2020-22015
Type: osv

## Details
Buffer Overflow vulnerability in FFmpeg 4.2 in mov_write_video_tag due to the out of bounds in libavformat/movenc.c, which could let a remote malicious user obtain sensitive information, cause a Denial of Service, or execute arbitrary code.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8190
