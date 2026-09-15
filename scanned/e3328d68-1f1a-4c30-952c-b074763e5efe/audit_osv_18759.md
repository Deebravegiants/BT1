# [M] CVE-2020-35964

## Summary
Severity: Medium
Advisory: CVE-2020-35964
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-01-03
Source: https://osv.dev/vulnerability/CVE-2020-35964
Type: osv

## Details
track_header in libavformat/vividas.c in FFmpeg 4.3.1 has an out-of-bounds write because of incorrect extradata packing.

## References
- https://security.gentoo.org/glsa/202105-24
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=26622
- https://github.com/FFmpeg/FFmpeg/commit/27a99e2c7d450fef15594671eef4465c8a166bd7
