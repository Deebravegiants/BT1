# [H] Incorrect privilege assignment in composite databases

## Summary
Severity: High
Advisory: BIT-neo4j-2026-1497
Aliases: BIT-neo4j-enterprise-2026-1497, CVE-2026-1497
Ecosystem: Bitnami
Published: 2026-05-14
Source: https://osv.dev/vulnerability/BIT-neo4j-2026-1497
Type: osv

## Affected
- Bitnami: `neo4j` — affected >=2025.1.0 <2026.2.0

## Details
Incorrect resolving of namespaces in composite databases in Neo4j Enterprise edition prior to versions 2026.02 and 5.26.22 can lead to the following scenario: 
an admin that intends to give a user an access to a remote database constituent "namespace.name" will inadvertently grant access to any local database or remote alias called "name". If such database or alias doesn't exist when the command is run, the privileges will apply if it's created in the future.

## References
- https://neo4j.com/security/CVE-2026-1497
- https://nvd.nist.gov/vuln/detail/CVE-2026-1497
