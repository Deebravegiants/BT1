# [C] BIT-appsmith-2024-55964

## Summary
Severity: Critical
Advisory: BIT-appsmith-2024-55964
Aliases: CVE-2024-55964, GHSA-m95x-4w54-gc83
Ecosystem: Bitnami
Published: 2025-04-02
Source: https://osv.dev/vulnerability/BIT-appsmith-2024-55964
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=0 <1.52.0

## Details
An issue was discovered in Appsmith before 1.52. An incorrectly configured PostgreSQL instance in the Appsmith image leads to remote command execution inside the Appsmith Docker container. The attacker must be able to access Appsmith, login to it, create a datasource, create a query against that datasource, and execute that query.

## References
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-m95x-4w54-gc83
- https://nvd.nist.gov/vuln/detail/CVE-2024-55964
