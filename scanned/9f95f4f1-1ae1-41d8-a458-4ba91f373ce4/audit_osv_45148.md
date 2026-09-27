# [H] FFmpeg v.n6.1-3-g466799d4f5 allows a heap-based buffer overflow via the `ff_gaussian_blur_8`...

## Summary
Severity: High
Advisory: JLSEC-2025-131
Ecosystem: Julia
CVSS: 8.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-131
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <7.1.0+0

## Details
FFmpeg v.n6.1-3-g466799d4f5 allows a heap-based buffer overflow via the `ff_gaussian_blur_8` function in `libavfilter/edge_template.c:116:5` component.

## References
- https://ffmpeg.org/
- https://github.com/FFmpeg/FFmpeg
- https://github.com/FFmpeg/FFmpeg/commit/162b4c60c8f72be2e93b759f3b1e14652b70b3ba
- https://github.com/FFmpeg/FFmpeg/commit/c443658d26d2b8e19901f9507a890e0efca79056
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://trac.ffmpeg.org/ticket/10699
