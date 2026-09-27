# [H] n8n before 2.36.2 Expression Sandbox Bypass via SpreadElement

## Summary
Severity: High
Advisory: CVE-2026-85165
Aliases: GHSA-fg85-4wv2-p98j
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85165
Type: osv

## Details
n8n versions before 2.36.2 contain an expression sandbox bypass vulnerability where free identifiers in spread, computed-key, switch-case, or class-extension positions resolve against process globals. Authenticated users with workflow-edit permission can mutate host objects through expression evaluation, with changes persisting process-wide until restart.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85165.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-fg85-4wv2-p98j
- https://nvd.nist.gov/vuln/detail/CVE-2026-85165
- https://www.vulncheck.com/advisories/n8n-before-2.36.2-expression-sandbox-bypass-via-spreadelement
