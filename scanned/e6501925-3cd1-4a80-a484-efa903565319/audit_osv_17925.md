# [H] CVE-2020-21688

## Summary
Severity: High
Advisory: CVE-2020-21688
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-10
Source: https://osv.dev/vulnerability/CVE-2020-21688
Type: osv

## Details
A heap-use-after-free in the av_freep function in libavutil/mem.c of FFmpeg 4.2 allows attackers to execute arbitrary code.

## References
- https://www.debian.org/security/2021/dsa-4998
- https://trac.ffmpeg.org/ticket/8186
