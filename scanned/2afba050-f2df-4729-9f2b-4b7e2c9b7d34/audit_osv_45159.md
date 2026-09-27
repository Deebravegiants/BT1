# [M] A flaw was found in FFmpeg's TTY Demuxer

## Summary
Severity: Medium
Advisory: JLSEC-2025-142
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-142
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <6.1.1+0
- Julia: `FFplay_jll` — affected >=0 <7.1.0+0

## Details
A flaw was found in FFmpeg's TTY Demuxer. This vulnerability allows possible data exfiltration via improper parsing of non-TTY-compliant input files in HLS playlists.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2334338
- https://lists.debian.org/debian-lts-announce/2025/07/msg00004.html
