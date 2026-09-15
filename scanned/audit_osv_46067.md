# [M] JLSEC-2026-641

## Summary
Severity: Medium
Advisory: JLSEC-2026-641
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-641
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <8.0.0+0
- Julia: `FFplay_jll` — affected >=0 <8.1.2+0

## Details
A NULL pointer dereference vulnerability exists in FFmpeg’s Firequalizer filter (`libavfilter/af_firequalizer.c`) due to a missing check on the return value of `av_malloc_array()` in the `config_input()` function. An attacker could exploit this by tricking a victim into processing a crafted media file with the Firequalizer filter enabled, causing the application to dereference a NULL pointer and crash, leading to denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2025-10256
- https://bugzilla.redhat.com/show_bug.cgi?id=2394495
- https://github.com/FFmpeg/FFmpeg/commit/a25462482c02c004d685a8fcf2fa63955aaa0931
- https://github.com/FFmpeg/FFmpeg/commit/d3be186ed1bcdcf2c093d6b13a0e66dc5132be2a
