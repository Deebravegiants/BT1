# [M] Ffmpeg: hls unsafe file extension bypass in ffmpeg

## Summary
Severity: Medium
Advisory: CVE-2023-6601
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2023-6601
Type: osv

## Details
A flaw was found in FFmpeg's HLS demuxer. This vulnerability allows bypassing unsafe file extension checks and triggering arbitrary demuxers via base64-encoded data URIs appended with specific file extensions.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00004.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6601.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6601
- https://bugzilla.redhat.com/show_bug.cgi?id=2253172
- https://github.com/FFmpeg/FFmpeg
