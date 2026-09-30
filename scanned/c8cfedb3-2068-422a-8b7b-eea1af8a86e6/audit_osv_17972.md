# [M] CVE-2020-22049

## Summary
Severity: Medium
Advisory: CVE-2020-22049
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2020-22049
Type: osv

## Details
A Denial of Service vulnerability exists in FFmpeg 4.2 due to a memory leak in the wtvfile_open_sector function in wtvdec.c.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commitdiff%3Bh=373c1c9b691fd4c6831b3a114a006b639304c2af
- https://lists.debian.org/debian-lts-announce/2021/11/msg00012.html
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8314
