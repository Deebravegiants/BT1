# [M] JLSEC-2026-639

## Summary
Severity: Medium
Advisory: JLSEC-2026-639
Ecosystem: Julia
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-639
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=7.1.0+0 <8.1.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <8.1.0+0
- Julia: `FFplay_jll` — affected >=7.1.0+0 <8.1.2+0

## Details
Buffer Overflow vulnerability in Ffmpeg v.N113007-g8d24a28d06 allows a local attacker to execute arbitrary code via the `libavfilter/avf_showwaves.c:722:24` in `showwaves_filter_frame`

## References
- https://ffmpeg.org/
- https://github.com/FFmpeg/FFmpeg
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://trac.ffmpeg.org/ticket/10756
