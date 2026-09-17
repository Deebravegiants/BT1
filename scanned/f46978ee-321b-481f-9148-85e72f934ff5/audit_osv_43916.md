# [M] CodeWhale before 0.8.64 Path Traversal via image_analyze symlink

## Summary
Severity: Medium
Advisory: CVE-2026-75914
Aliases: GHSA-w7wx-5q49-r59w
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75914
Type: osv

## Details
CodeWhale versions before 0.8.64 contain a path traversal vulnerability in the image_analyze tool that fails to canonicalize symlinks before reading files. Attackers can create workspace symlinks pointing to external files with image extensions to leak file bytes to the vision endpoint without user approval.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75914.json
- https://github.com/Hmbown/CodeWhale/security/advisories/GHSA-w7wx-5q49-r59w
- https://nvd.nist.gov/vuln/detail/CVE-2026-75914
- https://www.vulncheck.com/advisories/codewhale-before-path-traversal-via-image-analyze-symlink
- https://github.com/Hmbown/CodeWhale/commit/26de44a8bd5051f8f944ea60b2c37ae1d2b7d25e
