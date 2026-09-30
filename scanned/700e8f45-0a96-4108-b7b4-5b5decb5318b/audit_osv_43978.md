# [H] n8n before 1.123.69 Expression Injection via Resource Locator

## Summary
Severity: High
Advisory: CVE-2026-77075
Aliases: GHSA-fh4c-9rr2-p7qc
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77075
Type: osv

## Details
n8n before 1.123.69, 2.x before 2.33.4, and 2.34.x before 2.34.1 contain an expression injection vulnerability in resource-locator field link preview rendering. The editor spliced the field's stored value directly into the node type's URL template without checking for expression syntax. An authenticated member can store a malicious value so that when another user opens the affected node in the editor, the injected expression is evaluated as JavaScript in the victim's authenticated session (cross-user script execution).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77075.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-fh4c-9rr2-p7qc
- https://nvd.nist.gov/vuln/detail/CVE-2026-77075
- https://www.vulncheck.com/advisories/n8n-before-expression-injection-via-resource-locator
