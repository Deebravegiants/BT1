# [C] SurrealDB server-takeover via SurrealQL injection on backup import

## Summary
Severity: Critical
Advisory: GHSA-ccj3-5p93-8p42
CWE: CWE-77
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-04-11
Source: https://github.com/advisories/GHSA-ccj3-5p93-8p42
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=2.2.0 <2.2.2
- crates.io: `surrealdb` — affected >=2.1.0 <2.1.5
- crates.io: `surrealdb` — affected >=0 <2.0.5

## Details
The SurrealDB command-line tool allows exporting databases through the `export` command. It was discovered that table or field names are not properly sanitized in exports, leading to a SurrealQL injection when the backup is reimported.

For the injection to occur, an authenticated System User with `OWNER` or `EDITOR` roles needs to create tables or fields with malicious names containing SurrealQL, subsequently exported using the `export` operation

The attacker could achieve a privilege escalation and root level access to the SurrealDB instance if a higher privileged user subsequently performs the `import` operation. 

Furthermore, applications using SurrealDB that allow its users to define custom fields or tables are at risk of a universal second order SurrealQL injection, even if query parameters are properly sanitized. 

This issue was discovered and patched during an code audit and penetration test of SurrealDB by cure53, the severity defined within cure53's preliminary finding is Critical, matched by our CVSS v4 assessment.

### Impact
This attack can be used to perform privilege escalation and complete takeover (root access) of the SurrealDB instance, as well as being able to perform SurrealQL injection attacks against co-tenanted applications where SurrealDB is used as a shared backend for multiple applications.

### Patches
A patch has been created that addresses the issue by fixing the bugs in the exporter which failed to escape some characters properly.

- Versions 2.0.5, 2.1.5, 2.2.2 and later are not affected by this issue.


### Workarounds
For SurrealDB users that are unable to upgrade, users that are looking to perform `import` operations must manually inspect the exported data for injected statements, prior to importing. 


### References
[SurrealDB Documentation - Export](https://surrealdb.com/docs/surrealdb/cli/export)
[SurrealDB Documentation - Import](https://surrealdb.com/docs/surrealdb/cli/import)
[SurrealDB Documentation - Authentication](https://surrealdb.com/docs/surrealdb/security/authentication)

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-ccj3-5p93-8p42
- https://github.com/surrealdb/surrealdb
