# [M] OpenBao's SQL Injection in PostgreSQL database secrets engine

## Summary
Severity: Medium
Advisory: GHSA-6vgr-cp5c-ffx3
CVE: CVE-2026-39946
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-6vgr-cp5c-ffx3
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20260420155735-b596b0882620

## Details
### Impact

When OpenBao revoked privileges on a role in the PostgreSQL database secrets engine, OpenBao failed to use proper database quoting on schema names provided by PostgreSQL. This could lead to role revocation failures, or more rarely, SQL injection as the management user.

This vulnerability was originally from HashiCorp Vault.

### Patches

This was addressed in v2.5.3.

### Workarounds

Audit table schemas and ensure database users cannot create new schemas and grant privileges on them.

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-6vgr-cp5c-ffx3
- https://nvd.nist.gov/vuln/detail/CVE-2026-39946
- https://github.com/openbao/openbao/pull/2931
- https://github.com/openbao/openbao/commit/80693a46ebb4fc2455f1c51ed1dd853b28c2fd77
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/releases/tag/v2.5.3
