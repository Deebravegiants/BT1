# [M] FFmpeg version n5.1 to n6.1 was discovered to contain an Off-by-one Error vulnerability in...

## Summary
Severity: Medium
Advisory: JLSEC-2025-127
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-127
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <7.1.0+0

## Details
FFmpeg version n5.1 to n6.1 was discovered to contain an Off-by-one Error vulnerability in `libavfilter/avf_showspectrum.c`. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted input.

## References
- https://gist.github.com/1047524396/dc2c64ffe0c3934a6176bcd2c5cf5656
- https://git.ffmpeg.org/gitweb/ffmpeg.git/blobdiff/aec67d3d7d2895bfea61aa1358d9d8e956f8615c..ab0fdaedd1e7224f7e84ea22fcbfaa4ca75a6c06:/libavfilter/avf_showspectrum.c
- https://git.ffmpeg.org/gitweb/ffmpeg.git/blobdiff/bf2d7b20ea1c7d15dcbaedd479f40295e5c83430..3061bf668feffc7c1f0b244205167b3b86da8015:/libavfilter/avf_showspectrum.c
- https://github.com/FFmpeg/FFmpeg/commit/3061bf668feffc7c1f0b244205167b3b86da8015
- https://github.com/FFmpeg/FFmpeg/commit/81df787b53eb5c6433731f6eaaf7f2a94d8a8c80
- https://github.com/ffmpeg/ffmpeg/commit/ab0fdaedd1e7224f7e84ea22fcbfaa4ca75a6c06
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
