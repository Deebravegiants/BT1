# [M] SurrealDB: Denial of Service via deep operator chains

## Summary
Severity: Medium
Advisory: GHSA-jv2j-mqmw-xvv5
CWE: CWE-674
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-jv2j-mqmw-xvv5
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=3.0.0 <3.1.5

## Details
An authenticated user could crash a SurrealDB server with a single query containing a long chain of operators.

Such a query — for example `RETURN 1 + 1 + 1 + ...` with tens of thousands of terms — is parsed into an expression tree one level deep per operator. Because the chain is flat and the pratt parser appends to it iteratively, the configured query- and object-recursion limits never fire, so the tree grows unbounded with the length of the query.

The root cause: the over-deep tree is later walked recursively, one call per node, when it is dropped, formatted, or lowered for execution — overflowing the thread stack and aborting the process.

### Impact

An authenticated user with query-execution privileges can crash a SurrealDB server with a single query containing a long chain of operators. The whole process aborts, denying service to every namespace and database on that instance until it is restarted. The crash occurs during query processing, before any data is read or written (availability only).

### Patches

A patch introduces a dedicated expression-depth budget — `expr_recursion_limit`, sourced from `max_expression_parsing_depth` (default 128, configurable via `SURREAL_MAX_EXPRESSION_PARSING_DEPTH`). It is charged once per pratt-parser level and once per operator appended to the spine, so an over-deep operator chain is rejected with a syntax error instead of building a tree that overflows the stack downstream. Paths that re-parse already-validated stored data are exempted, so existing databases with deep stored expressions still load.

- Versions 3.1.5 and later are not affected by this issue.

### Workarounds

Users unable to patch should consider the following workarounds:

- Restrict the ability of untrusted users to execute arbitrary queries via the `--deny-arbitrary-query` capability flag for the affected user classes (guest, record, or system).
- Restrict untrusted access to the WebSocket `/rpc` endpoint, which accepts larger request bodies than the HTTP `/sql` endpoint. The `/sql` endpoint's 1 MiB body limit lowers the achievable operator depth but does not by itself guarantee the stack cannot be exhausted.
- Run SurrealDB under an orchestrator or process manager that restarts it automatically on exit (e.g. Kubernetes, systemd `Restart=on-failure`, or a Docker restart policy), so the server recovers immediately after a crash. This limits downtime from a successful attack but does not prevent the crash.

### References

- [SurrealQL Documentation — Operators](https://surrealdb.com/docs/surrealql/operators)
- `fix(syn): bound expression operator-tree depth to prevent stack-overflow DoS`

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-jv2j-mqmw-xvv5
- https://github.com/surrealdb/surrealdb
