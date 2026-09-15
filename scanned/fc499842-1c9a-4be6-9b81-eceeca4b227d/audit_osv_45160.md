# [H] A flaw was found in FFmpeg's HLS playlist parsing

## Summary
Severity: High
Advisory: JLSEC-2025-143
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-143
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <6.1.1+0
- Julia: `FFplay_jll` — affected >=0 <7.1.0+0

## Details
A flaw was found in FFmpeg's HLS playlist parsing. This vulnerability allows a denial of service via a maliciously crafted HLS playlist that triggers a null pointer dereference during initialization.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2334335
