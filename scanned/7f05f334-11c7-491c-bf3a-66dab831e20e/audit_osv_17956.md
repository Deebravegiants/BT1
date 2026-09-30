# [M] CVE-2020-22028

## Summary
Severity: Medium
Advisory: CVE-2020-22028
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2020-22028
Type: osv

## Details
Buffer Overflow vulnerability exists in FFmpeg 4.2 in filter_vertically_8 at libavfilter/vf_avgblur.c, which could cause a remote Denial of Service.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8274
