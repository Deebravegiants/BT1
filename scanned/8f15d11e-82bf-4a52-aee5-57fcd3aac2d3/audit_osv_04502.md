# [M] Discourse's Fail-Open Access Control in Data Explorer Plugin Allows Unauthorized SQL Query Execution

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-28218
Aliases: CVE-2026-28218, GHSA-jxrc-72mr-mfh5
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-discourse-2026-28218
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.1

## Details
Discourse is an open source discussion platform. Prior to versions 2025.12.2, 2026.1.1, and 2026.2.0, fail-open access control in Data Explorer plugin allows any authenticated user to execute SQL queries that have no explicit group assignments, including built-in system queries. Versions 2025.12.2, 2026.1.1, and 2026.2.0 patch the issue. As a workaround, either explicitly set group permissions on each Data Explorer query that doesn't have permissions, or disable discourse-data-explorer plugin.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-jxrc-72mr-mfh5
- https://nvd.nist.gov/vuln/detail/CVE-2026-28218
