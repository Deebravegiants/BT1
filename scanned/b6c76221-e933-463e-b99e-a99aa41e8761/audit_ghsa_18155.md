# [M] SurrealDB is Vulnerable to Unauthorized Data Exposure via LIVE Query Subscriptions

## Summary
Severity: Medium
Advisory: GHSA-7vm2-j586-vcvc
CVE: CVE-2025-11060
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-11
Source: https://github.com/advisories/GHSA-7vm2-j586-vcvc
Type: github-advisory

## Affected
- crates.io: `SurrealDB` — affected >=2.3.0 <2.3.8
- crates.io: `SurrealDB` — affected >=2.2.0 <2.2.8
- crates.io: `SurrealDB` — affected >=0 <2.1.9
- crates.io: `SurrealDB` — affected >=3.0.0-alpha.0 <3.0.0-alpha.8

## Details
`LIVE SELECT` statements are used to capture changes to data within a table in real time. Documents included in `WHERE` conditions and `DELETE` notifications were not properly reduced to respect the querying user's security context. Instead the leaked documents reflect the context of the user triggering the notification.

This allows a record or guest user with permissions to run live query subscriptions on a table to observe unauthorised records within the same table, when another user is altering or deleting these records, bypassing access controls.

### Impact
A record or guest user with permissions to run live query subscriptions on a table is able to observe unauthorised records within the same table, with unauthorised records returned when deleted, or when records matching the WHERE conditions are created, updated, or deleted, by another user. This impacts confidentiality, limited to the table the attacker has access to, and with the data disclosed dependent of the actions taken by other users.

### Patches
A patch has been created for the following versions:

- Versions 2.1.9, 2.2.8 and 2.3.8 and later are not affected by this issue. 
- The first release following v3.0.0-alpha.7 will be patched.

### Workarounds
Assess the impact of users with permissions on table records effectively having full read access to the table, use separate tables if required, with impacts to functionality.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-7vm2-j586-vcvc
- https://nvd.nist.gov/vuln/detail/CVE-2025-11060
- https://github.com/surrealdb/surrealdb/pull/6247
- https://github.com/surrealdb/surrealdb/commit/d81169a06b89f0c588134ddf2d62eeb8d5e8fd0c
- https://access.redhat.com/security/cve/CVE-2025-11060
- https://bugzilla.redhat.com/show_bug.cgi?id=2394708
- https://github.com/surrealdb/surrealdb
- https://surrealdb.com/docs/surrealql/statements/live
