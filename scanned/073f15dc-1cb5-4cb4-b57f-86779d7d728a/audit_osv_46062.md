# [H] JLSEC-2026-636

## Summary
Severity: High
Advisory: JLSEC-2026-636
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-636
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=7.1.0+0 <8.1.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <8.1.0+0
- Julia: `FFplay_jll` — affected >=7.1.0+0 <8.1.2+0

## Details
Buffer Overflow vulnerability in Ffmpeg v.N113007-g8d24a28d06 allows a local attacker to execute arbitrary code via the `libavfilter/af_stereowiden.c:120:69`.

## References
- https://trac.ffmpeg.org/ticket/10746
