# [H] FFmpeg version n6.1.1 has a double-free vulnerability in the `fftools/ffmpeg_mux_init.c` component...

## Summary
Severity: High
Advisory: JLSEC-2025-144
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-144
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <6.1.2+0

## Details
FFmpeg version n6.1.1 has a double-free vulnerability in the `fftools/ffmpeg_mux_init.c` component of FFmpeg, specifically within the `new_stream_audio` function.

## References
- https://gist.github.com/1047524396/d7d4ea8055b75c4a9f9bbcff31d21423
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/fftools/ffmpeg_mux_init.c#L886
- https://github.com/ffmpeg/ffmpeg/commit/ced5c5fdb8634d39ca9472a2026b2d2fea16c4e5
