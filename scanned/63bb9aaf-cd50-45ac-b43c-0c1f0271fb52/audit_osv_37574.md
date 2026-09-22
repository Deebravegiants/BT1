# [H] LibreChat Server-Side Request Forgery using DNS resolution

## Summary
Severity: High
Advisory: CVE-2026-31945
Aliases: GHSA-f92m-jpv7-55p2
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-31945
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. Versions 0.8.2-rc2 through 0.8.2 are vulnerable to a server-side request forgery (SSRF) attack when using agent actions or MCP. Although a previous SSRF vulnerability (https://github.com/danny-avila/LibreChat/security/advisories/GHSA-rgjq-4q58-m3q8) was reported and patched, the fix only introduced hostname validation. It does not verify whether DNS resolution results in a private IP address. As a result, an attacker can still bypass the protection and gain access to internal resources, such as an internal RAG API or cloud instance metadata endpoints. Version 0.8.3-rc1 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31945.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-f92m-jpv7-55p2
- https://nvd.nist.gov/vuln/detail/CVE-2026-31945
