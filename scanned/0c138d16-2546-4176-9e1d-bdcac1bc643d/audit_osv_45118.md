# [M] FFMPEG version 4.1 contains a CWE-129: Improper Validation of Array Index vulnerability in...

## Summary
Severity: Medium
Advisory: JLSEC-2025-101
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-101
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <4.3.1+0

## Details
FFMPEG version 4.1 contains a CWE-129: Improper Validation of Array Index vulnerability in `libavcodec/cbs_av1.c` that can result in Denial of service. This attack appears to be exploitable via specially crafted AV1 file has to be provided as input. This vulnerability appears to have been fixed in after commit b97a4b658814b2de8b9f2a3bce491c002d34de31.

## References
- https://github.com/FFmpeg/FFmpeg/commit/b97a4b658814b2de8b9f2a3bce491c002d34de31#diff-cd7e24986650014d67f484f3ffceef3f
