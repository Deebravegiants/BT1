# [H] CVE-2020-22036

## Summary
Severity: High
Advisory: CVE-2020-22036
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2020-22036
Type: osv

## Details
A heap-based Buffer Overflow vulnerability exists in FFmpeg 4.2 in filter_intra at libavfilter/vf_bwdif.c, which might lead to memory corruption and other potential consequences.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8261
