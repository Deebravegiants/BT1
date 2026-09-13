# [M] exists/2 predicate silently dropped on limited relationships with a parent() filter in AshSql

## Summary
Severity: Medium
Advisory: CVE-2026-77454
Aliases: EEF-CVE-2026-77454, GHSA-8v9m-8pxv-738c
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-77454
Type: osv

## Details
Incorrect Authorization vulnerability in ash-project ash_sql allows a caller to bypass a scoping or authorization filter expressed as exists/2 over a relationship that declares both a limit (or from_many?) and a parent(...)-referencing filter or sort.

AshSql.Join.related_query/3 skips the caller-supplied exists predicate for such relationships and delegates it to limit_from_many/5. When the relationship's own filter or sort references parent(...), limit_from_many/5 takes a branch that drops both the limit and the predicate, emitting a bare correlated EXISTS with no predicate. The check then matches any record that has any related row. Most severely, when the expression backs a policy (for example authorize_if expr(exists(memberships, user_id == ^actor(:id)))), the actor-scoping condition disappears and the policy passes for any actor with any related row.

This issue affects ash_sql: from 0.4.1 before 0.7.1.

## References
- https://cna.erlef.org/cves/CVE-2026-77454.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-77454
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77454.json
- https://github.com/ash-project/ash_sql/security/advisories/GHSA-8v9m-8pxv-738c
- https://nvd.nist.gov/vuln/detail/CVE-2026-77454
- https://github.com/ash-project/ash_sql/commit/865fdd4e5e70724a23b19c048e6768c31d2209ab
- https://github.com/ash-project/ash_sql
