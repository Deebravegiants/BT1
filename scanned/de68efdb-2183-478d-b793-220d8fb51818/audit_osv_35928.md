# [C] pgAdmin 4: AI Assistant read-only transaction bypass via sqlparse/PostgreSQL lexer disagreement (incomplete fix for CVE-2026-12045)

## Summary
Severity: Critical
Advisory: CVE-2026-17351
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-17351
Type: osv

## Details
The fix for CVE-2026-12045 in pgAdmin 4 9.16 required the LLM-supplied query passed to the AI Assistant's execute_sql_query tool to parse, via sqlparse, as exactly one non-transaction-control statement before running it inside a BEGIN TRANSACTION READ ONLY wrapper. sqlparse's string-literal lexing can disagree with PostgreSQL's own parser: under standard_conforming_strings = on (PostgreSQL's default since 9.1), a backslash immediately before a quote is an ordinary character to PostgreSQL, but sqlparse treats it as escaping the quote. A payload such as SELECT '\';COMMIT;CREATE TABLE pwn(x int);SELECT 1 --' therefore parses as a single SELECT to sqlparse's validator, while PostgreSQL executes it as four statements: the smuggled COMMIT ends the wrapping read-only transaction, and the trailing ROLLBACK becomes a no-op. This reintroduces the same write/RCE bypass CVE-2026-12045 was meant to close, reachable via the same indirect prompt-injection delivery (an attacker plants the payload in any object the AI Assistant may read; the LLM emits it as a tool call).

An initial candidate fix ran the query with psycopg's execute(..., prepare=True), intending to force PostgreSQL's own Parse step (extended query protocol) to reject multi-statement text regardless of sqlparse's classification. This candidate fix does not work as submitted: psycopg3's PrepareManager silently ignores the prepare argument whenever the connection's prepare_threshold is None, which is pgAdmin's default for every server connection (the per-server "Prepare threshold" field is blank unless an administrator explicitly sets it) -- psycopg3 falls back to the simple query protocol, the same multi-statement-capable path the bypass exploits, so the candidate fix closes nothing on any real-world default configuration.

The corrected fix sets conn.prepare_threshold = 0 directly on the dedicated, single-use read-only connection the AI Assistant tool opens, structurally forcing the extended query protocol independent of any server-level configuration. Verified against a live PostgreSQL 18 instance: the payload executes successfully under the prepare_threshold=None (default) behavior, and is rejected with "cannot insert multiple commands into a prepared statement" once prepare_threshold=0 is set on that connection.

This issue affects pgAdmin 4: from 9.13 before 9.17.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17351.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-17351
- https://github.com/pgadmin-org/pgadmin4/issues/10192
- https://github.com/pgadmin-org/pgadmin4/commit/bf4792444446f0e7ab721d23cbd6bfe6afaa7a8b
- https://github.com/pgadmin-org/pgadmin4/commit/ef76102bcd1cdb544eb9b4ef18d3382f22b76752
- https://github.com/pgadmin-org/pgadmin4
