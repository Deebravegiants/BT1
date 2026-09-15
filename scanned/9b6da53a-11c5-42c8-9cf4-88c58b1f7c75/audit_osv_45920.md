# [H] JLSEC-2026-476

## Summary
Severity: High
Advisory: JLSEC-2026-476
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-476
Type: osv

## Affected
- Julia: `mpv_jll` — affected >=0 <0.41.0+0

## Details
A format string vulnerability in mpv through 0.33.0 allows user-assisted remote attackers to achieve code execution via a crafted m3u playlist file.

## References
- https://devel0pment.de/?p=2217
- https://github.com/mpv-player/mpv/commit/d0c530919d8cd4d7a774e38ab064e0fabdae34e6
- https://github.com/mpv-player/mpv/releases/tag/v0.33.1
- https://mpv.io
- https://security.gentoo.org/glsa/202107-46
