# [H] OpenSift: Insufficient URL destination restrictions in ingest flow could enable SSRF-style internal access

## Summary
Severity: High
Advisory: CVE-2026-28677
Aliases: GHSA-5jfc-p787-2mf9
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-28677
Type: osv

## Details
OpenSift is an AI study tool that sifts through large datasets using semantic search and generative AI. Prior to version 1.6.3-alpha, the URL ingest pipeline accepted user-controlled remote URLs with incomplete destination restrictions. Although private/local host checks existed, missing restrictions for credentialed URLs, non-standard ports, and cross-host redirects left SSRF-class abuse paths in non-localhost deployments. This issue has been patched in version 1.6.3-alpha.

## References
- https://github.com/OpenSift/OpenSift/releases/tag/v1.6.3-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28677.json
- https://github.com/OpenSift/OpenSift/security/advisories/GHSA-5jfc-p787-2mf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-28677
- https://github.com/OpenSift/OpenSift/commit/1126e0a503876056a68a434e19f64158a5a4840b
- https://github.com/OpenSift/OpenSift/commit/de99b9c
- https://github.com/OpenSift/OpenSift/pull/67
