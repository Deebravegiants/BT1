# [H] Arc has an authenticated arbitrary local-file read via DuckDB I/O functions that bypasses RBAC table-level checks

## Summary
Severity: High
Advisory: GHSA-p2j4-c4g6-rpf5
CVE: CVE-2026-47735
CWE: CWE-200, CWE-22, CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-p2j4-c4g6-rpf5
Type: github-advisory

## Affected
- Go: `github.com/basekick-labs/arc` — affected >=0 <0.0.0-20260520141557-91bdc29d1a02

## Details
### Summary

Arc's user-SQL validator (`internal/api/query.go:ValidateSQLRequest`) blocked only `read_parquet(` and `arc_partition_agg(` via regex denylist. The broader DuckDB I/O function family — `read_csv_auto`, `read_csv`, `read_json`, `read_json_auto`, `read_text`, `read_blob`, `glob`, `parquet_metadata`, `parquet_schema`, `read_xlsx`, etc. — was not blocked. RBAC table-reference extraction inspected only `FROM`/`JOIN` clauses, so scalar table functions in the `SELECT` list slipped past both layers.

### Impact

Any authenticated user, including a token with `permissions: []`, can read arbitrary local files via:

```
POST /api/v1/query
Authorization: Bearer <token>
{"sql": "SELECT * FROM read_csv_auto('/etc/passwd', header=false, columns={'l':'VARCHAR'}) LIMIT 5"}
```

Confirmed reachable targets:

- `auth.db` — bcrypt hashes for every API token, plus legacy SHA-256 rows.
- `arc.toml` — S3 secrets, TLS keys.
- `/proc/self/environ` — environment-variable secrets.
- Cross-tenant Parquet files — bypasses RBAC because the tenant scope is enforced at the table layer, not on raw file paths.
- SSRF when `httpfs` is loaded (any S3-backed deployment) — `read_csv_auto('http://169.254.169.254/latest/meta-data/...')` reaches instance metadata IPs.

### Patches

Fixed in 2026.06.1 (PR #442) via a structural sandbox at the DuckDB layer:

1. `SET GLOBAL allowed_directories = [...]` enumerates Arc's legitimate filesystem prefixes (storage roots + tier prefixes + import upload dir + compaction temp).
2. `SET GLOBAL enable_external_access = false` (one-way at runtime).
3. Verified by reading back the flag.

After lockdown, DuckDB refuses to open any file outside the allowlist and refuses further `INSTALL`/`LOAD`. Already-loaded extensions remain callable.

### Workarounds

- Restrict API access to known-trusted networks via firewall rules.
- Temporary mitigation: add `read_csv*`/`read_json*`/`glob` etc. to `dangerousSQLPattern` in `internal/api/query.go` pending 2026.06.1.

### Credits

Reported by Alex Manson ([@NeuroWinter](https://github.com/NeuroWinter), https://neurowinter.com/) on 2026-05-19.

## References
- https://github.com/Basekick-Labs/arc/security/advisories/GHSA-p2j4-c4g6-rpf5
- https://github.com/Basekick-Labs/arc/pull/442
- https://github.com/Basekick-Labs/arc/commit/91bdc29d1a02178ccf8c66375eccf85203108dfb
- https://github.com/Basekick-Labs/arc
