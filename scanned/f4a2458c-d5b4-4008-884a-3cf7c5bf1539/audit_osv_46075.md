# [H] JLSEC-2026-650

## Summary
Severity: High
Advisory: JLSEC-2026-650
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-650
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <8.1.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <8.1.0+0
- Julia: `FFplay_jll` — affected >=0 <8.1.2+0

## Details
An improper resource deallocation and closure vulnerability in the `tools/zmqsend.c` component of FFmpeg v8.0.1 allows attackers to cause a Denial of Service (DoS) via supplying a crafted input file.

## References
- https://excellent-oatmeal-319.notion.site/CVE-2026-30998-Resource-Leak-3265a71f9cca4dc58df4632ce8b60a50
- https://ffmpeg.org/doxygen/7.0/zmqsend_8c_source.html
- https://github.com/FFmpeg/FFmpeg/blob/master/tools/zmqsend.c
