# [M] Ffmpeg: improper handling of input format in tty demuxer of ffmpeg

## Summary
Severity: Medium
Advisory: CVE-2023-6602
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-12-31
Source: https://osv.dev/vulnerability/CVE-2023-6602
Type: osv

## Details
A flaw was found in FFmpeg's TTY Demuxer. This vulnerability allows possible data exfiltration via improper parsing of non-TTY-compliant input files in HLS playlists.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00004.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6602.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6602
- https://bugzilla.redhat.com/show_bug.cgi?id=2334338
- https://github.com/FFmpeg/FFmpeg
