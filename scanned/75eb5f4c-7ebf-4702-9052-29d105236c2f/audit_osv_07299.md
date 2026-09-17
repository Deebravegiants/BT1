# [H] BIT-postgresql-2020-10733

## Summary
Severity: High
Advisory: BIT-postgresql-2020-10733
Aliases: CVE-2020-10733
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2020-10733
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=12.0.0 <12.3.0

## Details
The Windows installer for PostgreSQL 9.5 - 12 invokes system-provided executables that do not have fully-qualified paths. Executables in the directory where the installer loads or the current working directory take precedence over the intended executables. An attacker having permission to add files into one of those directories can use this to execute arbitrary code with the installer's administrative rights.

## References
- https://security.netapp.com/advisory/ntap-20201001-0006/
- https://www.postgresql.org/about/news/2038/
- https://www.postgresql.org/support/security/11/
- https://nvd.nist.gov/vuln/detail/CVE-2020-10733
