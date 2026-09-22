# [M] OpenSift: Sensitive implementation details exposed via raw exception messages and token-returning endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-28675
Aliases: GHSA-667g-rvcj-w976
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-28675
Type: osv

## Details
OpenSift is an AI study tool that sifts through large datasets using semantic search and generative AI. Prior to version 1.6.3-alpha, some endpoints returned raw exception strings to clients. Additionally, login token material was exposed in UI/rendered responses and token rotation output. This issue has been patched in version 1.6.3-alpha.

## References
- https://github.com/OpenSift/OpenSift/releases/tag/v1.6.3-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28675.json
- https://github.com/OpenSift/OpenSift/security/advisories/GHSA-667g-rvcj-w976
- https://nvd.nist.gov/vuln/detail/CVE-2026-28675
- https://github.com/OpenSift/OpenSift/commit/1126e0a503876056a68a434e19f64158a5a4840b
- https://github.com/OpenSift/OpenSift/commit/de99b9c
- https://github.com/OpenSift/OpenSift/pull/67
