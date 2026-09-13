# [H] Ffmpeg: null pointer dereference in ffmpeg hls parsing

## Summary
Severity: High
Advisory: CVE-2023-6603
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-31
Source: https://osv.dev/vulnerability/CVE-2023-6603
Type: osv

## Details
A flaw was found in FFmpeg's HLS playlist parsing. This vulnerability allows a denial of service via a maliciously crafted HLS playlist that triggers a null pointer dereference during initialization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6603.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6603
- https://bugzilla.redhat.com/show_bug.cgi?id=2334335
- https://github.com/FFmpeg/FFmpeg
