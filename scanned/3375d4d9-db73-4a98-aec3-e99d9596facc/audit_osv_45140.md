# [H] `libavcodec/pthread_frame.c` in FFmpeg before 5.1.2, as used in VLC and other products, leaves stale...

## Summary
Severity: High
Advisory: JLSEC-2025-123
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-123
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <6.1.1+0
- Julia: `FFplay_jll` — affected >=0 <7.1.0+0

## Details
`libavcodec/pthread_frame.c` in FFmpeg before 5.1.2, as used in VLC and other products, leaves stale hwaccel state in worker threads, which allows attackers to trigger a use-after-free and execute arbitrary code in some circumstances (e.g., hardware re-initialization upon a mid-video SPS change when Direct3D11 is used).

## References
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/cc867f2c09d2b69cee8a0eccd62aff002cbbfe11
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KOMB6WRUC55VWV25IKJTV22KARBUGWGQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PQHNSWXFUN3VJ3AO2AEJUK3BURSGM5G2/
- https://news.ycombinator.com/item?id=35356201
- https://security.gentoo.org/glsa/202312-14
- https://wrv.github.io/h26forge.pdf
