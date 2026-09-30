# [M] Ffmpeg: hls xbin demuxer dos amplification in ffmpeg

## Summary
Severity: Medium
Advisory: CVE-2023-6604
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2023-6604
Type: osv

## Details
A flaw was found in FFmpeg. This vulnerability allows unexpected additional CPU load and storage consumption, potentially leading to degraded performance or denial of service via the demuxing of arbitrary data as XBIN-formatted data without proper format validation.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00004.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6604.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6604
- https://bugzilla.redhat.com/show_bug.cgi?id=2334337
- https://github.com/FFmpeg/FFmpeg
