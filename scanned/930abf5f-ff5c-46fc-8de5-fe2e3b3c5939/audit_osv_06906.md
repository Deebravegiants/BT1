# [M] Improper Access Control Allowing Cross-User Session Metadata Disclosure in $listSessions Aggregation Stage

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-13061
Aliases: CVE-2026-13061
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13061
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An authenticated user may be able to view session metadata belonging to other users on the system through the $listSessions aggregation stage. This information is normally restricted to users with cluster-level administrative privileges, and includes active session identifiers, associated usernames, and activity timestamps.

## References
- https://jira.mongodb.org/browse/SERVER-127689
- https://nvd.nist.gov/vuln/detail/CVE-2026-13061
