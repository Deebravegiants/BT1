# [H] OpenSift: Insufficient path containment checks in storage helpers could allow path traversal-style file operations

## Summary
Severity: High
Advisory: CVE-2026-28676
Aliases: GHSA-ww4m-c7hv-2rqv
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-28676
Type: osv

## Details
OpenSift is an AI study tool that sifts through large datasets using semantic search and generative AI. Prior to version 1.6.3-alpha, multiple storage helpers used path construction patterns that did not uniformly enforce base-directory containment. This created path-injection risk in file read/write/delete flows if malicious path-like values were introduced. This issue has been patched in version 1.6.3-alpha.

## References
- https://github.com/OpenSift/OpenSift/releases/tag/v1.6.3-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28676.json
- https://github.com/OpenSift/OpenSift/security/advisories/GHSA-ww4m-c7hv-2rqv
- https://nvd.nist.gov/vuln/detail/CVE-2026-28676
- https://github.com/OpenSift/OpenSift/commit/1126e0a503876056a68a434e19f64158a5a4840b
- https://github.com/OpenSift/OpenSift/commit/de99b9c
- https://github.com/OpenSift/OpenSift/pull/67
