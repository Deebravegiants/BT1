# [M] CrewAI < 1.15.1 SSRF Filter Bypass via HTTP Redirect in Scrape Tools

## Summary
Severity: Medium
Advisory: CVE-2026-62240
Aliases: GHSA-mr4r-hcgx-8p4h, PYSEC-2026-3819
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62240
Type: osv

## Details
CrewAI before 1.15.1 contains a server-side request forgery vulnerability in the validate_url function that performs one-shot DNS resolution and blocklist checks before returning the original URL unchanged. Attackers can bypass the security filter by supplying URLs that redirect to internal addresses or use DNS rebinding techniques to access internal services and cloud metadata endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62240.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-62240
- https://www.vulncheck.com/advisories/crewai-ssrf-filter-bypass-via-http-redirect-in-scrape-tools
- https://github.com/crewAIInc/crewAI/issues/6520
- https://github.com/crewAIInc/crewAI/commit/5d4851eac797cafc45b726f65747fe2c9520fc42
- https://github.com/crewAIInc/crewAI/pull/6331
- https://github.com/crewAIInc/crewAI/releases/tag/1.15.1
- https://github.com/crewAIInc/crewAI
