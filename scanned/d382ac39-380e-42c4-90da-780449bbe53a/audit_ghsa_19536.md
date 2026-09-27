# [H] SurrealDB has uncaught exception in Net module that leads to database crash

## Summary
Severity: High
Advisory: GHSA-rq86-9m6r-cm3g
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-10
Source: https://github.com/advisories/GHSA-rq86-9m6r-cm3g
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=2.2.0 <2.2.2
- crates.io: `surrealdb` — affected >=2.1.0 <2.1.5
- crates.io: `surrealdb` — affected >=0 <2.0.5

## Details
A vulnerability was found where an attacker can crash the database via crafting a HTTP query that returns a null byte. The problem relies on an uncaught exception in the `net` module, where the result of the query will be converted to JSON before showing as the HTTP response to the user in the **/sql** endpoint.

### Impact
This vulnerability allows any authenticated user to crash a SurrealDB instance by sending a crafted query with a null byte to the /sql endpoint. 

Where SurrealDB is used as an application backend, it is possible that an application user can crash the SurrealDB instance and thus the supported application through crafted inputs that exploit this attack vector.


### Patches
A patch has been introduced that ensures the error is caught and converted as an error.
- Versions 2.2.2, 2.1.5 and 2.0.5 and later are not affected by this isssue

### Workarounds

Affected users who are unable to update may want to limit the ability of untrusted clients to run arbitrary queries in the affected versions of SurrealDB. To limit the impact of the denial of service, SurrealDB administrators may also want to ensure that the SurrealDB process is running so that it can be automatically re-started after a crash.

Where SurrealDB is used as an application backend, ensure sanitisation of input at the application layer to prevent injection attacks.

### References
https://github.com/surrealdb/surrealdb/pull/5647

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-rq86-9m6r-cm3g
- https://github.com/surrealdb/surrealdb/pull/5647
- https://github.com/surrealdb/surrealdb
