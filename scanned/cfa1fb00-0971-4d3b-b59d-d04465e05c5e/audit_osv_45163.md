# [M] A flaw was found in FFmpeg's HLS demuxer

## Summary
Severity: Medium
Advisory: JLSEC-2025-146
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-146
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <6.1.1+0
- Julia: `FFplay_jll` — affected >=0 <7.1.0+0

## Details
A flaw was found in FFmpeg's HLS demuxer. This vulnerability allows bypassing unsafe file extension checks and triggering arbitrary demuxers via base64-encoded data URIs appended with specific file extensions.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2253172
- https://lists.debian.org/debian-lts-announce/2025/07/msg00004.html
