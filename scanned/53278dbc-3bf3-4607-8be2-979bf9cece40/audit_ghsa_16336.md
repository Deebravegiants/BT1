# [M] Uncaught Exception Handling Parsing Errors on Line Terminators

## Summary
Severity: Medium
Advisory: GHSA-8xff-473h-f863
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-8xff-473h-f863
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <1.2.1

## Details
The span rendering would panic when handling failed parsing of queries where the error occurred on a line terminator character.

### Impact

A client that is authorized to run queries in a SurrealDB server is able to execute a malformed query which will fail to parse on a line terminator character and cause a panic in the span rendering code. This will crash the server, leading to denial of service.

### Patches

- Version 1.2.1 and later are not affected by this issue.

### Workarounds

Concerned users unable to update may want to limit the ability of untrusted users to run arbitrary SurrealQL queries in the affected versions of SurrealDB. To limit the impact of the denial of service, SurrealDB administrators may also want to ensure that the SurrealDB process is running so that it can be automatically re-started after a crash.

### References

- #3527
- https://github.com/StarlaneStudios/Surrealist/issues/177

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-8xff-473h-f863
- https://github.com/StarlaneStudios/Surrealist/issues/177
- https://github.com/surrealdb/surrealdb
