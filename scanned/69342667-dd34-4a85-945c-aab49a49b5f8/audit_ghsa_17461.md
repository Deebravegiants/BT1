# [H] Neuron MySQLSelectTool “read-only” bypass via `SELECT ... INTO OUTFILE` (file write → potential RCE)

## Summary
Severity: High
Advisory: GHSA-j8g6-5gqc-mq36
CVE: CVE-2025-67509
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-j8g6-5gqc-mq36
Type: github-advisory

## Affected
- Packagist: `neuron-core/neuron-ai` — affected >=0 <2.8.12

## Details
### Impact

`MySQLSelectTool` is intended to be a read-only SQL tool (e.g., for LLM agent querying). However, validation based on the first keyword (e.g., `SELECT`) and a forbidden-keyword list does not block file-writing constructs such as `INTO OUTFILE` / `INTO DUMPFILE`.  

As a result, an attacker who can influence the tool input (e.g., prompt injection through a public agent endpoint) may be able to write arbitrary content to files on the DB server.

If the MySQL/MariaDB account has the `FILE` privilege and server configuration permits writes to a useful location (e.g., a web-accessible directory), the impact can escalate to remote code execution on the application host (for example, by writing a PHP web shell).

**Who is impacted:** Deployments that expose an agent using `MySQLSelectTool` to untrusted input and run with overly-permissive DB privileges/configuration.

### Patches

**Not patched in:** 2.8.11  

**Fixed in:** 2.8.12

Recommended fix direction:

- Explicitly reject queries containing: `INTO`, `OUTFILE`, `DUMPFILE`, `LOAD_FILE`, and other file/IO-related functions/clauses.

- Prefer AST-based validation (SQL parser) over keyword checks.

- Constrain allowed tables/columns and disallow multi-statements.

### Workarounds

If you cannot upgrade immediately:

- Remove/disable `MySQLSelectTool` for any agent reachable from untrusted input.

- Ensure DB account used by the tool **does not** have `FILE` privilege.

- Ensure `secure_file_priv` is set to a directory that is **not** web-accessible (or restrict it tightly).

- Add a defensive query filter at the application layer rejecting `INTO OUTFILE`, `INTO DUMPFILE`, `LOAD_FILE`, `;` (multi-statements), and suspicious comment patterns.

## References
- https://github.com/neuron-core/neuron-ai/security/advisories/GHSA-j8g6-5gqc-mq36
- https://nvd.nist.gov/vuln/detail/CVE-2025-67509
- https://github.com/neuron-core/neuron-ai/commit/72735d0ea133266cf2f5d5d195d41e9dd865289a
- https://github.com/neuron-core/neuron-ai
- https://github.com/neuron-core/neuron-ai/releases/tag/2.8.12
