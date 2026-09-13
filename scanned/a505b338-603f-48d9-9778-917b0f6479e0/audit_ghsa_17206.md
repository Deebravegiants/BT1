# [H] pgx SQL Injection via Line Comment Creation

## Summary
Severity: High
Advisory: GHSA-m7wr-2xf7-cm9p
CVE: CVE-2024-27289
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-04
Source: https://github.com/advisories/GHSA-m7wr-2xf7-cm9p
Type: github-advisory

## Affected
- Go: `github.com/jackc/pgx` — affected >=0 <4.18.2
- Go: `github.com/jackc/pgx/v4` — affected >=0 <4.18.2

## Details
### Impact

SQL injection can occur when all of the following conditions are met:

1. The non-default simple protocol is used.
2. A placeholder for a numeric value must be immediately preceded by a minus.
3. There must be a second placeholder for a string value after the first placeholder; both
must be on the same line.
4. Both parameter values must be user-controlled.

e.g. 

Simple mode must be enabled:

```go
// connection string includes "prefer_simple_protocol=true"
// or
// directly enabled in code
config.ConnConfig.PreferSimpleProtocol = true
```

Parameterized query:

```sql
SELECT * FROM example WHERE result=-$1 OR name=$2;
```

Parameter values:

`$1` => `-42`
`$2` => `"foo\n 1 AND 1=0 UNION SELECT * FROM secrets; --"`

Resulting query after preparation:

```sql
SELECT * FROM example WHERE result=--42 OR name= 'foo
1 AND 1=0 UNION SELECT * FROM secrets; --';
```

### Patches

The problem is resolved in v4.18.2.

### Workarounds

Do not use the simple protocol or do not place a minus directly before a placeholder.

## References
- https://github.com/jackc/pgx/security/advisories/GHSA-m7wr-2xf7-cm9p
- https://nvd.nist.gov/vuln/detail/CVE-2024-27289
- https://github.com/jackc/pgx/commit/f94eb0e2f96782042c96801b5ac448f44f0a81df
- https://github.com/jackc/pgx
- https://www.sonarsource.com/blog/double-dash-double-trouble-a-subtle-sql-injection-flaw
