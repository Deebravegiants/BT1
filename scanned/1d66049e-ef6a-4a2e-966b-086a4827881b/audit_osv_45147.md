# [H] FFmpeg v.n6.1-3-g466799d4f5 allows memory consumption when using the colorcorrect filter, in the...

## Summary
Severity: High
Advisory: JLSEC-2025-130
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-130
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <7.1.0+0

## Details
FFmpeg v.n6.1-3-g466799d4f5 allows memory consumption when using the colorcorrect filter, in the `av_malloc` function in `libavutil/mem.c:105:9` component.

## References
- https://github.com/FFmpeg/FFmpeg/commit/5f87a68cf70dafeab2fb89b42e41a4c29053b89b
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://trac.ffmpeg.org/ticket/10701
