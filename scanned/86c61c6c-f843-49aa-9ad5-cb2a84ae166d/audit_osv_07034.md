# [M] Caching of authentication context

## Summary
Severity: Medium
Advisory: BIT-neo4j-2026-1471
Aliases: BIT-neo4j-enterprise-2026-1471, CVE-2026-1471
Ecosystem: Bitnami
Published: 2026-05-29
Source: https://osv.dev/vulnerability/BIT-neo4j-2026-1471
Type: osv

## Affected
- Bitnami: `neo4j` — affected >=2025.1.0 <2026.1.4

## Details
Excessive caching of authentication context in Neo4j Enterprise edition versions prior to 2026.1.4 leads to authenticated users inheriting the context of the first user who authenticated after restart. The issue is limited to certain non-default configurations of SSO (UserInfo endpoint). 
We recommend upgrading to versions 2026.1.4 (or 5.26.22) where the issue is fixed.

## References
- https://neo4j.com/security/CVE-2026-1471
- https://nvd.nist.gov/vuln/detail/CVE-2026-1471
