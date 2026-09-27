# [M] A flaw was found in FFmpeg

## Summary
Severity: Medium
Advisory: JLSEC-2025-148
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-148
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <6.1.1+0
- Julia: `FFplay_jll` — affected >=0 <7.1.0+0

## Details
A flaw was found in FFmpeg. This vulnerability allows unexpected additional CPU load and storage consumption, potentially leading to degraded performance or denial of service via the demuxing of arbitrary data as XBIN-formatted data without proper format validation.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2334337
- https://lists.debian.org/debian-lts-announce/2025/07/msg00004.html
