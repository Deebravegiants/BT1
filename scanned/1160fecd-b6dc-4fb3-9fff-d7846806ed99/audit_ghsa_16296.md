# [M] Uncaught Exception in Macro Expecting Native Function to Exist

## Summary
Severity: Medium
Advisory: GHSA-6wr5-jmpr-mjcx
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-6wr5-jmpr-mjcx
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <1.2.0

## Details
The query executor would panic when executing a query containing a call to a built-in SurrealDB function that did not exist. This could occur accidentally in situations where the version of the SurrealDB client was newer than the SurrealDB server or when a pre-parsed query was provided to the server via a newer version of the SurrealDB SDK.

### Impact

A client that is authorized to run queries in a SurrealDB server is able to craft and execute a pre-parsed query invoking a nonexistent built-in function, which will cause a panic. This will crash the server, leading to denial of service.

### Patches

- Version 1.2.0 and later are not affected by this issue.

### Workarounds

Concerned users unable to update may want to limit the ability of untrusted users to run arbitrary SurrealQL queries in the affected versions of SurrealDB. To limit the impact of the denial of service, SurrealDB administrators may also want to ensure that the SurrealDB process is running so that it can be automatically re-started after a crash.

### References

- #3454
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=65755

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-6wr5-jmpr-mjcx
- https://github.com/surrealdb/surrealdb/pull/3454
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=65755
- https://github.com/surrealdb/surrealdb
