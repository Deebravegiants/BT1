# [M] CVE-2020-22044

## Summary
Severity: Medium
Advisory: CVE-2020-22044
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2020-22044
Type: osv

## Details
A Denial of Service vulnerability exists in FFmpeg 4.2 due to a memory leak in the url_open_dyn_buf_internal function in libavformat/aviobuf.c.

## References
- https://lists.debian.org/debian-lts-announce/2021/11/msg00012.html
- https://trac.ffmpeg.org/ticket/8295
