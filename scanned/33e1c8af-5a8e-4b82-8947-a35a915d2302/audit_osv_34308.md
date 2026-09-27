# [M] Firecrawl SSRF Vulnerability via malicious webhook

## Summary
Severity: Medium
Advisory: CVE-2025-57818
Aliases: GHSA-p2wg-prhf-jx79
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-08-26
Source: https://osv.dev/vulnerability/CVE-2025-57818
Type: osv

## Details
Firecrawl turns entire websites into LLM-ready markdown or structured data. Prior to version 2.0.1, a server-side request forgery (SSRF) vulnerability was discovered in Firecrawl's webhook functionality. Authenticated users could configure a webhook to an internal URL and send POST requests with arbitrary headers, which may have allowed access to internal systems. This has been fixed in version 2.0.1. If upgrading is not possible, it is recommend to isolate Firecrawl from any sensitive internal systems.

## References
- https://github.com/firecrawl/firecrawl/releases/tag/v2.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57818.json
- https://github.com/firecrawl/firecrawl/security/advisories/GHSA-p2wg-prhf-jx79
- https://nvd.nist.gov/vuln/detail/CVE-2025-57818
- https://github.com/firecrawl/firecrawl/commit/b15fae51a760e9810a66bbfde5d5693d0df3fbeb
- https://github.com/firecrawl/firecrawl/commit/e8cf0985b07968061a6b684b58097732e827ed46
