# [M] FFmpeg v.n6.1-3-g466799d4f5 allows an attacker to trigger use of a parameter of negative size in the...

## Summary
Severity: Medium
Advisory: JLSEC-2025-128
Ecosystem: Julia
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-128
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <7.1.0+0

## Details
FFmpeg v.n6.1-3-g466799d4f5 allows an attacker to trigger use of a parameter of negative size in the `av_samples_set_silence` function in `thelibavutil/samplefmt.c:260:9` component.

## References
- https://github.com/FFmpeg/FFmpeg/commit/b1942734c7cbcdc9034034373abcc9ecb9644c47
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://trac.ffmpeg.org/ticket/10700
