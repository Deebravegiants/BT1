# [H] Authenticated SQL injection in the metrics-service retention policy subsystem of mcp-gateway-registry

## Summary
Severity: High
Advisory: CVE-2026-14471
Aliases: GHSA-79qc-vqfr-xx5q
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-14471
Type: osv

## Details
Improper Neutralization of Special Elements in the metrics-service retention policy management component in Amazon mcp-gateway-registry before 1.0.13 might allow an authenticated remote user to execute arbitrary SQL queries via a crafted table_name value that is interpolated into SQL statements in identifier position.



To remediate this issue, users should upgrade to version 1.0.13 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-052-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14471.json
- https://github.com/agentic-community/mcp-gateway-registry/security/advisories/GHSA-79qc-vqfr-xx5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-14471
- https://github.com/agentic-community/mcp-gateway-registry/releases/tag/v1.0.13
