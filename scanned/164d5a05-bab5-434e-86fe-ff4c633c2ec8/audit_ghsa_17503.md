# [M] uptrace pgdriver SQL injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h4h6-vccr-44h2
CVE: CVE-2024-44906
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-06-12
Source: https://github.com/advisories/GHSA-h4h6-vccr-44h2
Type: github-advisory

## Affected
- Go: `github.com/uptrace/bun/driver/pgdriver` — affected >=0 <1.2.15

## Details
uptrace pgdriver v1.2.1 was discovered to contain a SQL injection vulnerability via the appendArg function in `/pgdriver/format.go`. The maintainer has stated that the issue is fixed in v1.2.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-44906
- https://github.com/uptrace/bun/issues/1224
- https://github.com/uptrace/bun/commit/8067a8f13f8d22fb57b76d6800f7aefc12b044cd
- https://github.com/uptrace/bun
- https://github.com/uptrace/bun/blob/1573ae7c2fffad1a7f72fd2d205e924b2fd4043b/driver/pgdriver/format.go#L62
- https://github.com/uptrace/bun/blob/v1.2.15/CHANGELOG.md
- https://github.com/uptrace/bun/tree/master/driver/pgdriver
- https://media.defcon.org/DEF%20CON%2032/DEF%20CON%2032%20presentations/DEF%20CON%2032%20-%20Paul%20Gerste%20-%20SQL%20Injection%20Isn%27t%20Dead%20Smuggling%20Queries%20at%20the%20Protocol%20Level.pdf
- https://www.sonarsource.com/blog/double-dash-double-trouble-a-subtle-sql-injection-flaw
