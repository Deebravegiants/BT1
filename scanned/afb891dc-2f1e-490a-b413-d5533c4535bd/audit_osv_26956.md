# [H] Ffmpeg: dash playlist ssrf vulnerability in ffmpeg

## Summary
Severity: High
Advisory: CVE-2023-6605
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2023-6605
Type: osv

## Details
A flaw was found in FFmpeg's DASH playlist support. This vulnerability allows arbitrary HTTP GET requests to be made on behalf of the machine running FFmpeg via a crafted DASH playlist containing malicious URLs.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00004.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6605.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6605
- https://bugzilla.redhat.com/show_bug.cgi?id=2334336
- https://github.com/FFmpeg/FFmpeg
