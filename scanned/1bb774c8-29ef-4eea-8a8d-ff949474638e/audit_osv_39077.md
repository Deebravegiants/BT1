# [H] Cornac < 2.6.0 Path Traversal via _extract_archive() in download.py

## Summary
Severity: High
Advisory: CVE-2026-43637
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-43637
Type: osv

## Details
Cornac before 2.6.0 contains a path traversal (Tar Slip) vulnerability that allows attackers to write arbitrary files outside the intended cache directory by supplying a crafted TAR archive containing ../ sequences, absolute paths, or symlink/hardlink entries to the _extract_archive() function in cornac/utils/download.py. Attackers can trigger this vulnerability through the built-in dataset loaders, which automatically download and extract archives, causing archive.extractall() to write files to arbitrary locations on the filesystem accessible to the running process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43637.json
- https://github.com/PreferredAI/cornac/releases/tag/v2.6.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-43637
- https://www.vulncheck.com/advisories/cornac-path-traversal-via-extract-archive-in-download-py
- https://github.com/PreferredAI/cornac/pull/709
- https://github.com/PreferredAI/cornac/commit/8a50be72c11569b6747c6b96d6e31a0a1962f1a8
- https://github.com/PreferredAI/cornac
