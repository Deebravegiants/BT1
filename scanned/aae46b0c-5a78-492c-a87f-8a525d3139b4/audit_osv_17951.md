# [H] CVE-2020-22023

## Summary
Severity: High
Advisory: CVE-2020-22023
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-22023
Type: osv

## Details
A heap-based Buffer Overflow vulnerabililty exists in FFmpeg 4.2 in filter_frame at libavfilter/vf_bitplanenoise.c, which might lead to memory corruption and other potential consequences.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8244
