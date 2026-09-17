# [H] IBAX go-ibax vulnerable to SQL injection

## Summary
Severity: High
Advisory: GHSA-g23g-mw97-65c8
CVE: CVE-2022-3802
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-g23g-mw97-65c8
Type: github-advisory

## Affected
- Go: `github.com/IBAX-io/go-ibax` — affected >=0 <1.4.2

## Details
SQL Injection vulnerability in `/packages/api/database.go` of go-ibax via `where` parameter allows attacker to spoof identity, tamper with existing data, allow the complete disclosure of all data on the system, destroy the data or make it otherwise unavailable, and become administrators of the database server. This issue affects versions starting from commits on Jul 18, 2020.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3802
- https://github.com/IBAX-io/go-ibax/issues/2063
- https://github.com/IBAX-io/go-ibax/commit/b0183d8e550836dc50282ee74ff421ee41b25a37
- https://github.com/IBAX-io/go-ibax
- https://vuldb.com/?id.212638
