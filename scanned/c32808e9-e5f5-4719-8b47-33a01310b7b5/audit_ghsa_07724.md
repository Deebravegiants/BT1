# [M] SurrealDB vulnerable to Denial of Service through scripting function memory edge case

## Summary
Severity: Medium
Advisory: GHSA-xx7m-69ff-9crp
CWE: CWE-476
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-xx7m-69ff-9crp
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <2.6.1
- crates.io: `surrealdb` — affected >=3.0.0-alpha.8 <3.0.0-beta.3

## Details
In SurrealDB instances with the scripting capability enabled (`--allow-scripting`),  users with the ability to run arbitrary queries can trigger a server crash due to a memory-safety bug in the underlying JS engine. The SurrealDB instance terminates instantly, requiring a manual restart.

The query consists of using built-in string functions to construct a large string and passing it to the JavaScript runtime for compilation. The exact string size required to trigger the crash varies between SurrealDB versions.

Whilst exploiting the vulnerability requires users to be able to run arbitrary queries, if guest access (`--allow-guests`), is enabled, then guests can perform this attack.

### Impact

Any user able to execute queries on a SurrealDB instance with scripting enabled (`--allow-scripting`) can cause complete denial of service. The server process terminates immediately without graceful shutdown.

The underlying cause of the vulnerability is a null pointer dereference in the `QuickJS-NG` v0.8 JavaScript engine, this vulnerability cannot be exploited to execute arbitrary code, or compromise the integrity or confidentiality of data. 

### Patches

Versions prior to SurrealDB `v2.6.1` and `v3.0.0-beta.3` are vulnerable.

The patches for SurrealDB `v2.6.1` and `v3.0.0-beta.3` update the `rquickjs` dependency from `v0.9.0` to `v0.11.0`, which in turn uses an updated version of `QuickJS-NG`.

### Workarounds
Deny execution of embedded scripting functions through the configuration of [capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities#capabilities) by starting SurrealDB with the `--deny-scripting` flag or the equivalent environment variable `SURREAL_CAPS_DENY_SCRIPT=true`. This has a usability implication, although scripting functions are disabled by default.

Administrators can also use `--deny-arbitrary-query`  to deny arbitrary querying by either `guest`, `record` or `system` users, or a combination of those, with impacts to functionality for those users. 

### Links ###
[SurrealDB Documentation - Capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities)
[SurrealDB Documentation - Guest Access](https://surrealdb.com/docs/surrealdb/security/capabilities#guest-access)
[SurrealQL Documentation - Scripting Functions](https://surrealdb.com/docs/surrealql/functions/script)
[quickjs-ng v0.9 Release Notes](https://github.com/quickjs-ng/quickjs/releases/tag/v0.9.0)
https://github.com/surrealdb/surrealdb/pull/6833
https://github.com/surrealdb/surrealdb/pull/6774

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-xx7m-69ff-9crp
- https://github.com/surrealdb/surrealdb/pull/6774
- https://github.com/surrealdb/surrealdb/pull/6833
- https://github.com/surrealdb/surrealdb/commit/2b0389b92398d9ecff4632cd51bbf8303832a988
- https://github.com/surrealdb/surrealdb/commit/bcd2ece9ef0d721215f06a47280698669f332285
- https://github.com/surrealdb/surrealdb
