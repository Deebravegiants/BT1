# [M] MindsDB through 26.1.0 Unauthenticated SSRF via Web Crawler

## Summary
Severity: Medium
Advisory: CVE-2026-86173
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86173
Type: osv

## Details
MindsDB through 26.1.0 contains a server-side request forgery vulnerability in the web crawler handler that allows unauthenticated attackers to fetch arbitrary URLs by supplying caller-controlled URLs to CrawlerTable.list. Attackers can bypass the allowlist control by exploiting the default empty configuration and access internal services and cloud metadata endpoints without authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86173.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86173
- https://www.vulncheck.com/advisories/mindsdb-through-26.1.0-unauthenticated-ssrf-via-web-crawler
- https://github.com/mindsdb/mindshub/issues/12480
- https://github.com/mindsdb/mindshub
- https://github.com/mindsdb/mindshub/blob/v26.1.0/mindsdb/integrations/handlers/web_handler/web_handler.py#L50-L65
- https://github.com/mindsdb/mindshub/blob/v26.1.0/mindsdb/utilities/config.py#L273
