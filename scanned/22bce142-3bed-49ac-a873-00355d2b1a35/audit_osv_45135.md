# [M] An integer overflow vulnerability was found in FFmpeg versions before 4.4.2 and before 5.0.1 in...

## Summary
Severity: Medium
Advisory: JLSEC-2025-119
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-119
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.3.1+0 <4.4.2+0
- Julia: `FFplay_jll` — affected >=0 <4.4.4+0

## Details
An integer overflow vulnerability was found in FFmpeg versions before 4.4.2 and before 5.0.1 in `g729_parse()` in `llibavcodec/g729_parser.c` when processing a specially crafted file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2076764
- https://security.gentoo.org/glsa/202312-14
- https://trac.ffmpeg.org/ticket/9651
