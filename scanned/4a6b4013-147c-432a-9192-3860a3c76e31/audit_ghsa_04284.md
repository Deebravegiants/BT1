# [C] Openshift Migration Advisor agent-API fails to validate JWT source_id claim, allowing cross-tenant data manipulation

## Summary
Severity: Critical
Advisory: GHSA-2fqw-7c6r-2cq6
CVE: CVE-2026-53471
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-2fqw-7c6r-2cq6
Type: github-advisory

## Affected
- Go: `github.com/kubev2v/migration-planner` — affected >=0 <0.13.5

## Details
A flaw was found in migration-planner. The agent-API middleware processes JSON Web Tokens (JWTs) for authentication, but its UpdateSourceInventory and UpdateAgentStatus handlers fail to validate the source_id claim within these tokens against the requested source ID. This oversight allows an authenticated attacker with a valid agent token to manipulate data across different tenants, leading to a complete collapse of tenant isolation. This could result in unauthorized overwriting of victim inventory, planting of malicious credential URLs, or corruption of migration assessments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53471
- https://github.com/kubev2v/migration-planner/pull/1213
- https://github.com/kubev2v/migration-planner/commit/fd21a239216f5eeec635d16c72be9c033bd5d1aa
- https://access.redhat.com/security/cve/CVE-2026-53471
- https://bugzilla.redhat.com/show_bug.cgi?id=2487070
- https://github.com/kubev2v/migration-planner
