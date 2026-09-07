# [H] SurrealDB Affected by Confused Deputy Privilege Escalation through Future Fields and Functions

## Summary
Severity: High
Advisory: GHSA-3v2x-9xcv-2v2v
CWE: CWE-441
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-3v2x-9xcv-2v2v
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <2.5.0
- crates.io: `surrealdb` — affected >=3.0.0-alpha.1 <3.0.0-beta.3

## Details
Unprivileged users (for example, those with the database editor role) can create or modify fields in records that contain functions or `futures`. `Futures` are values which are only computed when the value is queried. The query executes in the context of the querying user, rather than the user who originally defined the future. Likewise, fields containing functions or custom-defined logic (`closures`) are executed under the privileges of the invoking user, not the creator.

This results in a confused deputy vulnerability: an attacker with limited privileges can define a malicious function or future field that performs privileged actions. When a higher-privileged user (such as a root owner or namespace administrator) executes the function or queries or modifies that record, the function executes with their elevated permissions. 

### Impact
An attacker who can create or update function/future fields can plant logic that executes with a privileged user’s context. If a privileged user performs a write that touches the malicious field, the attacker can achieve full privilege escalation (e.g., create a root owner and take over the server). 

If a privileged user performs a read action on the malicious field, this attack vector could still be potentially be used to perform limited denial of service or, in the specific case where the network capability was explicitly enabled and unrestricted, exfiltrate database information over the network.

### Patches

Versions prior to 2.5.0 and 3.0.0-beta.3 are vulnerable.

For SurrealDB 3.0, `futures` are no longer supported, replaced by `computed`  fields, only available within schemaful tables. 

Further to this patches for 2.5.0 and 3.0.0-beta.3: 
- Implements an `auth_limit` on defined apis, functions, fields and events, that limits execution to the permissions of the creating user or the invoking user, whichever is lower.
- Prevents `closures` from being stored, that eliminates a potential attack surface. For 2.5.0 this can still be allowed by using the `insecure_storable_closures` capability
- Ensures the proper auth level is used to compute expressions in signin & signup

**_For existing apis, events, fields and functions defined prior to upgrading to 2.5.0 or 3.0.0-beta.3 `auth_limit` will not apply, to avoid breaking changes. These will need to subsequently be redefined so that `auth_limit` can take effect._**

### Workarounds
Users unable to patch are advised to evaluate their use of the database to identify where low privileged users are able to define logic subsequently executed by privileged users, such as apis, functions, futures fields and events, and recommended to minimise these instances.

### References
[Futures](https://surrealdb.com/docs/surrealql/datamodel/futures)
[Closures](https://surrealdb.com/docs/surrealql/datamodel/closures)
[SurrealDB Environment Variables](https://surrealdb.com/docs/surrealdb/cli/env)

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-3v2x-9xcv-2v2v
- https://github.com/surrealdb/surrealdb/commit/f515c91363ee735aa1bc08580d9e7fa0de6e736f
- https://github.com/surrealdb/surrealdb
- https://github.com/surrealdb/surrealdb/releases/tag/v2.5.0
- https://github.com/surrealdb/surrealdb/releases/tag/v3.0.0-beta.2
