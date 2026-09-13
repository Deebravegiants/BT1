# [H] JLSEC-2026-651

## Summary
Severity: High
Advisory: JLSEC-2026-651
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-651
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <8.1.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <8.1.0+0
- Julia: `FFplay_jll` — affected >=0 <8.1.2+0

## Details
A heap buffer overflow in the `av_bprint_finalize()` function of FFmpeg v8.0.1 allows attackers to cause a Denial of Service (DoS) via a crafted input.

## References
- https://excellent-oatmeal-319.notion.site/CVE-2026-30999-Memory-Leak-e0d88ac53e2e42c1b5ef9aa3497e27b6
- https://ffmpeg.org/doxygen/7.0/zmqsend_8c_source.html
- https://github.com/FFmpeg/FFmpeg/blob/master/tools/zmqsend.c
- https://www.ffmpeg.org/download.html
