# [H] Denial of service in github.com/jackc/pgproto3/v2

## Summary
Severity: High
Advisory: GHSA-jqcq-xjh3-6g23
CVE: CVE-2026-32286
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-jqcq-xjh3-6g23
Type: github-advisory

## Affected
- Go: `github.com/jackc/pgproto3/v2` — affected >=2.0.0

## Details
The DataRow.Decode function fails to properly validate field lengths. A malicious or compromised PostgreSQL server can send a DataRow message with a negative field length, causing a slice bounds out of range panic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-32286
- https://github.com/golang/vulndb/issues/4518
- https://github.com/jackc/pgx/issues/2507
- https://bugzilla.redhat.com/show_bug.cgi?id=2448626
- https://github.com/jackc/pgproto3
- https://pkg.go.dev/vuln/GO-2026-4518
- https://securityinfinity.com/research/memory-safety-vulnerabilities-in-go-postgresql-wire-protocol-parsers-pgproto3-pgx
