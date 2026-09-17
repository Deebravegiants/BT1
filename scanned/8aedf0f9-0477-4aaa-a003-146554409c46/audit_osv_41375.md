# [M] SiYuan before v3.8.0 Secret Exfiltration via http_request URL

## Summary
Severity: Medium
Advisory: CVE-2026-59809
Aliases: GHSA-853m-gvvm-6rvx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-59809
Type: osv

## Details
SiYuan before v3.8.0 interpolates secret placeholders into the destination URL parameter of the http_request MCP tool, allowing attackers to exfiltrate stored secrets. An MCP client can craft a request with an attacker-controlled URL containing secret placeholders to send plaintext secret values to any public host without confirmation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59809.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-853m-gvvm-6rvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-59809
- https://www.vulncheck.com/advisories/siyuan-before-secret-exfiltration-via-http-request-url
