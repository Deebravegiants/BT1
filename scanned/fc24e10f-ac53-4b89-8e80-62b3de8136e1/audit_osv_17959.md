# [H] CVE-2020-22031

## Summary
Severity: High
Advisory: CVE-2020-22031
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-22031
Type: osv

## Details
A Heap-based Buffer Overflow vulnerability exists in FFmpeg 4.2 at libavfilter/vf_w3fdif.c in filter16_complex_low, which might lead to memory corruption and other potential consequences.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
- https://trac.ffmpeg.org/attachment/ticket/8243/gdb-vf_w3fdif_191
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8243
