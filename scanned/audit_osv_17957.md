# [H] CVE-2020-22029

## Summary
Severity: High
Advisory: CVE-2020-22029
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-22029
Type: osv

## Details
A heap-based Buffer Overflow vulnerability exists in FFmpeg 4.2 at libavfilter/vf_colorconstancy.c: in slice_get_derivative, which crossfade_samples_fltp, which might lead to memory corruption and other potential consequences.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commitdiff%3Bh=a7fd1279703683ebb548ef7baa2f1519994496ae
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8250
