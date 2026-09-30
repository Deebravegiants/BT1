# [M] n8n before 1.123.69 SSRF via Edit Image Node

## Summary
Severity: Medium
Advisory: CVE-2026-77074
Aliases: GHSA-233r-fpgw-fx8x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77074
Type: osv

## Details
n8n versions before 1.123.69 contain a server-side request forgery vulnerability in the Edit Image node's Draw Text operation that allows authenticated users to inject MVG primitives. Attackers can craft malicious text values to issue blind outbound HTTP requests to arbitrary addresses or access local files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77074.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-233r-fpgw-fx8x
- https://nvd.nist.gov/vuln/detail/CVE-2026-77074
- https://www.vulncheck.com/advisories/n8n-before-ssrf-via-edit-image-node
