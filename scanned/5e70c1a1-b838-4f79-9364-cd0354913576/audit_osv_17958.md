# [H] CVE-2020-22030

## Summary
Severity: High
Advisory: CVE-2020-22030
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-22030
Type: osv

## Details
A heap-based Buffer Overflow vulnerability exists in FFmpeg 4.2 at libavfilter/af_afade.c in crossfade_samples_fltp, which might lead to memory corruption and other potential consequences.

## References
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8276
