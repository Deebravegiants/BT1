# [M] Prior to ffmpeg version 4.3, the tty demuxer did not have a '`read_probe`' function assigned to it

## Summary
Severity: Medium
Advisory: JLSEC-2025-116
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-116
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <4.3.1+0

## Details
Prior to ffmpeg version 4.3, the tty demuxer did not have a '`read_probe`' function assigned to it. By crafting a legitimate "ffconcat" file that references an image, followed by a file the triggers the tty demuxer, the contents of the second file will be copied into the output file verbatim (as long as the `-vcodec copy` option is passed to ffmpeg).

## References
- https://github.com/FFmpeg/FFmpeg/commit/3bce9e9b3ea35c54bacccc793d7da99ea5157532#diff-74f6b92a0541378ad15de9c29c0a2b0c69881ad9ffc71abe568b88b535e00a7f
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
