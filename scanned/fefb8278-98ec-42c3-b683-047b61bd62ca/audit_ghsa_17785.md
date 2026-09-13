# [M] files.photo.gallery command injection

## Summary
Severity: Medium
Advisory: GHSA-5wjw-qjhm-v43h
CVE: CVE-2024-53615
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-30
Source: https://github.com/advisories/GHSA-5wjw-qjhm-v43h
Type: github-advisory

## Affected
- npm: `files.photo.gallery` — affected >=0.3.0

## Details
A command injection vulnerability in the video thumbnail rendering component of files.photo.gallery v0.3.0 through 0.11.0 allows remote attackers to execute arbitrary code via a crafted video file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53615
- https://github.com/beune/CVE-2024-53615
- https://github.com/mjau-mjau/files.photo.gallery
