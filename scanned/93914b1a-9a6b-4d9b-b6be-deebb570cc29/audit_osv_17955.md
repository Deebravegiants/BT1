# [H] CVE-2020-22027

## Summary
Severity: High
Advisory: CVE-2020-22027
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-22027
Type: osv

## Details
A heap-based Buffer Overflow vulnerability exits in FFmpeg 4.2 in deflate16 at libavfilter/vf_neighbor.c, which might lead to memory corruption and other potential consequences.

## References
- https://trac.ffmpeg.org/attachment/ticket/8242/gdb-vf_neighbor_191
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8242
