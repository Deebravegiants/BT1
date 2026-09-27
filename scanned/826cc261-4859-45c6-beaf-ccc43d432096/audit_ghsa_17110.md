# [H] pgx SQL Injection via Protocol Message Size Overflow

## Summary
Severity: High
Advisory: GHSA-mrww-27vc-gghv
CVE: CVE-2024-27304
CWE: CWE-190, CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-04
Source: https://github.com/advisories/GHSA-mrww-27vc-gghv
Type: github-advisory

## Affected
- Go: `github.com/jackc/pgx` — affected >=0 <4.18.2
- Go: `github.com/jackc/pgx` — affected >=5.0.0 <5.5.4
- Go: `github.com/jackc/pgx/v4` — affected >=0 <4.18.2
- Go: `github.com/jackc/pgx/v5` — affected >=5.0.0 <5.5.4

## Details
### Impact

SQL injection can occur if an attacker can cause a single query or bind message to exceed 4 GB in size. An integer overflow in the calculated message size can cause the one large message to be sent as multiple messages under the attacker's control.

### Patches

The problem is resolved in v4.18.2 and v5.5.4.

### Workarounds

Reject user input large enough to cause a single query or bind message to exceed 4 GB in size.

## References
- https://github.com/jackc/pgproto3/security/advisories/GHSA-7jwh-3vrq-q3m8
- https://github.com/jackc/pgx/security/advisories/GHSA-mrww-27vc-gghv
- https://nvd.nist.gov/vuln/detail/CVE-2024-27304
- https://github.com/jackc/pgproto3/commit/945c2126f6db8f3bea7eeebe307c01fe92bca007
- https://github.com/jackc/pgx/commit/adbb38f298c76e283ffc7c7a3f571036fea47fd4
- https://github.com/jackc/pgx/commit/c543134753a0c5d22881c12404025724cb05ffd8
- https://github.com/jackc/pgx/commit/f94eb0e2f96782042c96801b5ac448f44f0a81df
- https://github.com/jackc/pgx
- https://www.youtube.com/watch?v=Tfg1B8u1yvE
