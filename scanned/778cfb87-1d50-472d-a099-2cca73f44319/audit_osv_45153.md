# [M] In FFmpeg version n6.1.1, specifically within the `avcodec/speexdec.c` module, a potential security...

## Summary
Severity: Medium
Advisory: JLSEC-2025-136
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-136
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <6.1.2+0

## Details
In FFmpeg version n6.1.1, specifically within the `avcodec/speexdec.c` module, a potential security vulnerability exists due to insufficient validation of certain parameters when parsing Speex codec extradata. This vulnerability could lead to integer overflow conditions, potentially resulting in undefined behavior or crashes during the decoding process.

## References
- https://gist.github.com/1047524396/455093807666f2e351d674750c8cd0b8
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavcodec/speexdec.c#L1423
- https://github.com/ffmpeg/ffmpeg/commit/0895ef0d6d6406ee6cd158fc4d47d80f201b8e9c
