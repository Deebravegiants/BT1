# [C] Openshift Migration Advisor lacks proper authorization and filtering for its DELETE /api/v1/sources API

## Summary
Severity: Critical
Advisory: GHSA-6xvf-9742-48w2
CVE: CVE-2026-53469
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-6xvf-9742-48w2
Type: github-advisory

## Affected
- Go: `github.com/kubev2v/migration-planner` — affected >=0 <0.13.5

## Details
A flaw was found in migration-planner. An authenticated user can exploit this vulnerability by sending a DELETE request to the /api/v1/sources route, which lacks proper authorization and filtering. This allows for the destruction of all customer data, including sources, agents, and assessments, leading to a critical loss of availability and integrity across the entire SaaS platform.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53469
- https://github.com/kubev2v/migration-planner/pull/1227
- https://github.com/kubev2v/migration-planner/commit/db4c7857bd8f8e04747a5ea0efca04b0235d6e4a
- https://access.redhat.com/security/cve/CVE-2026-53469
- https://bugzilla.redhat.com/show_bug.cgi?id=2487065
- https://github.com/kubev2v/migration-planner
