# [H] JLSEC-2026-640

## Summary
Severity: High
Advisory: JLSEC-2026-640
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-640
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=7.1.0+0 <8.1.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <8.1.0+0
- Julia: `FFplay_jll` — affected >=7.1.0+0 <8.1.2+0

## Details
Buffer Overflow vulnerability in Ffmpeg v.N113007-g8d24a28d06 allows a local attacker to execute arbitrary code via a floating point exception (FPE) error at `libavfilter/vf_minterpolate.c:1078:60` in interpolate.

## References
- https://ffmpeg.org/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://trac.ffmpeg.org/ticket/10758
