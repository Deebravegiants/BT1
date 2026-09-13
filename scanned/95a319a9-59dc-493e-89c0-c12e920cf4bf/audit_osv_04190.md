# [H] ArangoDB - Insufficient Session Expiration after Password Change

## Summary
Severity: High
Advisory: BIT-arangodb-2021-25940
Aliases: CVE-2021-25940
Ecosystem: Bitnami
Published: 2025-03-10
Source: https://osv.dev/vulnerability/BIT-arangodb-2021-25940
Type: osv

## Affected
- Bitnami: `arangodb` — affected >=3.7.6 <3.8.4

## Details
In ArangoDB, versions v3.7.6 through v3.8.3 are vulnerable to Insufficient Session Expiration. When a user’s password is changed by the administrator, the session isn’t invalidated, allowing a malicious user to still be logged in and perform arbitrary actions within the system.

## References
- https://github.com/arangodb/arangodb/commit/e9c6ee9dcca7b9b4fbcd02a0b323d205bee838d3
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25940
- https://nvd.nist.gov/vuln/detail/CVE-2021-25940
