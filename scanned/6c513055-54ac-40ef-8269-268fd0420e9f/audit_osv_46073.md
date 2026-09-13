# [H] JLSEC-2026-649

## Summary
Severity: High
Advisory: JLSEC-2026-649
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-649
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <8.1.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <8.1.0+0
- Julia: `FFplay_jll` — affected >=0 <8.1.2+0

## Details
An out-of-bounds read in the `read_global_param()` function (`libavcodec/av1dec.c`) of FFmpeg v8.0.1 allows attackers to cause a Denial of Service (DoS) via a crafted input.

## References
- https://excellent-oatmeal-319.notion.site/CVE-2026-30997-Out-of-Bounds-Access-a7929817b9794568b2f7774397c7d65f
- https://github.com/FFmpeg/FFmpeg
