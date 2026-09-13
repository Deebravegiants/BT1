# [M] SigNoz < 0.133.0 - Cross-Organization Insecure Direct Object Reference in Alert Rules

## Summary
Severity: Medium
Advisory: CVE-2026-57956
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-57956
Type: osv

## Details
SigNoz before 0.133.0 contains a broken access control vulnerability that allows authenticated users to access other organizations' alert rules by supplying a target rule UUID, as the alert rule store predicates fail to filter by organization ID. Attackers can read, edit, and delete alert rules belonging to other organizations by exploiting the missing tenant isolation check, bypassing multi-tenant access controls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57956.json
- https://github.com/SigNoz/signoz/releases/tag/v0.133.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-57956
- https://www.vulncheck.com/advisories/signoz-cross-organization-insecure-direct-object-reference-in-alert-rules
- https://github.com/SigNoz/signoz/issues/11830
- https://github.com/SigNoz/signoz/pull/12117
- https://github.com/SigNoz/signoz
