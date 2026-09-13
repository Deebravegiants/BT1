# [M] Unchecked Return Value, Out-of-bounds Read vulnerability in FFmpeg allows Read Sensitive Constants...

## Summary
Severity: Medium
Advisory: JLSEC-2025-149
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-149
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=7.1.0+0 <7.1.1+0
- Julia: `FFplay_jll` — affected >=7.1.0+0 <7.1.1+0

## Details
Unchecked Return Value, Out-of-bounds Read vulnerability in FFmpeg allows Read Sensitive Constants Within an Executable. This vulnerability is associated with program files  https://github.Com/FFmpeg/FFmpeg/blob/master/libavfilter/af_pan.C .

This issue affects FFmpeg: 7.1.

Issue was fixed:  https://github.com/FFmpeg/FFmpeg/commit/b5b6391d64807578ab872dc58fb8aa621dcfc38a

https://github.com/FFmpeg/FFmpeg/commit/b5b6391d64807578ab872dc58fb8aa621dcfc38a This issue was discovered by: Simcha Kosman

## References
- https://github.com/FFmpeg/FFmpeg/commit/b5b6391d64807578ab872dc58fb8aa621dcfc38a
- https://lists.debian.org/debian-lts-announce/2025/02/msg00037.html
