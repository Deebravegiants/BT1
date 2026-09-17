# [M] CVE-2020-21697

## Summary
Severity: Medium
Advisory: CVE-2020-21697
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-10
Source: https://osv.dev/vulnerability/CVE-2020-21697
Type: osv

## Details
A heap-use-after-free in the mpeg_mux_write_packet function in libavformat/mpegenc.c of FFmpeg 4.2 allows to cause a denial of service (DOS) via a crafted avi file.

## References
- https://www.debian.org/security/2021/dsa-4998
- https://trac.ffmpeg.org/ticket/8188
