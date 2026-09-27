# [M] Lara Dashboard 0.9.2 through 1.3.1 Server-Side Request Forgery in Builder Markdown Fetch

## Summary
Severity: Medium
Advisory: CVE-2026-87821
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87821
Type: osv

## Details
Lara Dashboard through 1.3.1 contains a server-side request forgery vulnerability in the POST /api/admin/builder/markdown/fetch endpoint that allows any authenticated user to fetch arbitrary URLs and read the response body. Attackers can read internal HTTP services and cloud metadata including IAM credentials by supplying malicious URLs without host validation or redirect restrictions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87821.json
- https://github.com/laradashboard/laradashboard/releases/tag/v1.3.2
- https://github.com/laradashboard/laradashboard/security/advisories/GHSA-4xqv-4c27-6c4j
- https://github.com/laradashboard/laradashboard/security/advisories/GHSA-f36j-h77g-6wj8
- https://nvd.nist.gov/vuln/detail/CVE-2026-87821
- https://www.vulncheck.com/advisories/lara-dashboard-0.9.2-through-1.3.1-server-side-request-forgery-in-builder-markdown-fetch
- https://github.com/laradashboard/laradashboard/commit/738cc1a219ce459323ef1d09c3789075f1b8d2f2
- https://github.com/laradashboard/laradashboard
- https://github.com/laradashboard/laradashboard/blob/v0.9.2/app/Services/Builder/MarkdownFetchService.php
- https://github.com/laradashboard/laradashboard/blob/v1.3.1/app/Http/Controllers/Api/Builder/MarkdownController.php
- https://github.com/laradashboard/laradashboard/blob/v1.3.1/app/Services/Builder/MarkdownFetchService.php
- https://github.com/laradashboard/laradashboard/blob/v1.3.2/app/Support/Security/SafeUrlValidator.php
