# [H] Daptin: SQL injection via unvalidated goqu.L() calls in aggregate API

## Summary
Severity: High
Advisory: GHSA-rw2c-8rfq-gwfv
CVE: CVE-2026-41422
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-rw2c-8rfq-gwfv
Type: github-advisory

## Affected
- Go: `github.com/daptin/daptin` — affected >=0 <0.11.4

## Details
## Summary

The `/aggregate/:typename` endpoint accepted `column` and `group` query parameters that were passed verbatim to `goqu.L()` — a raw SQL literal expression builder — without any validation. This bypassed all parameterization and allowed authenticated users with any valid session to inject arbitrary SQL expressions.

## Impact

An authenticated low-privilege user could:
- Extract data from any table via subquery: `(SELECT group_concat(email) FROM user_account) as leak`
- Disclose database internals: `sqlite_version()`, `(SELECT sql FROM sqlite_master)`
- Exfiltrate cross-table data via correlated subqueries

The vulnerability was confirmed locally; `user_account.email` values were extracted via a crafted `column` parameter by a non-admin user.

## Root Cause

`goqu.L(userInput)` in `server/resource/resource_aggregate.go` inserted user-supplied query parameters directly into the SQL string with no validation.

## Fix (v0.11.4)

All `goqu.L()` calls on user-controlled input were eliminated and replaced with:
- Structural expression parsing supporting all documented API forms
- Schema-based column validation (column names checked against entity schema via `TableInfo().GetColumnByName()`)
- Exact-match allowlist for aggregate functions (`count`, `sum`, `avg`, `min`, `max`, `first`, `last`) and scalar functions (`date`, `strftime`, `upper`, `lower`, etc.)
- Safe goqu constructors (`goqu.I()`, `goqu.SUM()`, `goqu.Func()`) for all generated expressions
- `allowedTables` scope enforcement: qualified column refs (`table.col`) validated against root entity + explicitly joined tables only

Two additional DoS bugs were fixed in the same commit: `uuid.MustParse` panic on malformed UUID input and an index-out-of-range panic in `ToOrderedExpressionArray` on empty sort expressions.

## Credits

Reported by @VashuVats.

## References
- https://github.com/daptin/daptin/security/advisories/GHSA-rw2c-8rfq-gwfv
- https://nvd.nist.gov/vuln/detail/CVE-2026-41422
- https://github.com/daptin/daptin
- https://github.com/daptin/daptin/releases/tag/v0.11.4
