# [H] A flaw was found in FFmpeg's DASH playlist support

## Summary
Severity: High
Advisory: JLSEC-2025-147
Ecosystem: Julia
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-147
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <6.1.1+0
- Julia: `FFplay_jll` — affected >=0 <7.1.0+0

## Details
A flaw was found in FFmpeg's DASH playlist support. This vulnerability allows arbitrary HTTP GET requests to be made on behalf of the machine running FFmpeg via a crafted DASH playlist containing malicious URLs.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2334336
- https://lists.debian.org/debian-lts-announce/2025/07/msg00004.html
