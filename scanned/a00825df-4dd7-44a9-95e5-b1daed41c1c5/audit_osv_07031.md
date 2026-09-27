# [M] BIT-neo4j-2024-34517

## Summary
Severity: Medium
Advisory: BIT-neo4j-2024-34517
Aliases: BIT-neo4j-enterprise-2024-34517, CVE-2024-34517, GHSA-p343-9qwp-pqxv
Ecosystem: Bitnami
Published: 2025-03-12
Source: https://osv.dev/vulnerability/BIT-neo4j-2024-34517
Type: osv

## Affected
- Bitnami: `neo4j` — affected >=5.0.0 <5.20.0

## Details
The Cypher component in Neo4j 5.0.0 through 5.18 mishandles IMMUTABLE privileges in some situations where an attacker already has admin access.

## References
- https://github.com/advisories/GHSA-p343-9qwp-pqxv
- https://github.com/neo4j/neo4j/wiki/Neo4j-5-changelog#cypher
- https://neo4j.com/security/cve-2024-34517/
- https://trust.neo4j.com
- https://nvd.nist.gov/vuln/detail/CVE-2024-34517
