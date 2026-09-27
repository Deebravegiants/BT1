# [H] CVE-2020-22032

## Summary
Severity: High
Advisory: CVE-2020-22032
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-22032
Type: osv

## Details
A heap-based Buffer Overflow vulnerability exists FFmpeg 4.2 at libavfilter/vf_edgedetect.c in gaussian_blur, which might lead to memory corruption and other potential consequences.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8275
- https://cwe.mitre.org/data/definitions/122.html
