# [M] Apify Actors MCP Server before 0.9.12 Server-Side Request Forgery via get-html-skeleton

## Summary
Severity: Medium
Advisory: CVE-2026-81093
Aliases: GHSA-m28f-9v8h-gg2f
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81093
Type: osv

## Details
The get-html-skeleton tool fetched a URL the caller supplied after checking only its syntax. The handler in src/tools/common/get_html_skeleton.ts validated the url argument with isValidHttpUrl from src/utils/generic.ts, which confirmed the string began with an http or https scheme and parsed as a URL and inspected neither the host name nor the address it resolves to. Loopback, link-local and private ranges therefore passed, including the address cloud providers use to serve instance metadata. The unchecked URL was handed to the web-browser actor and the fetched document was returned in the tool response, so any caller of the MCP server could make it request an endpoint reachable only from the host and read the result, including instance credentials. Version 0.9.12 removes the tool.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81093.json
- https://github.com/apify/apify-mcp-server/security/advisories/GHSA-m28f-9v8h-gg2f
- https://nvd.nist.gov/vuln/detail/CVE-2026-81093
- https://www.vulncheck.com/advisories/apify-actors-mcp-server-before-0.9.12-server-side-request-forgery-via-get-html-skeleton
- https://github.com/apify/apify-mcp-server/pull/572
- https://github.com/apify/apify-mcp-server
