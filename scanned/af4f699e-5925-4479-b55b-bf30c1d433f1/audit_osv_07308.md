# [H] BIT-postgresql-2021-23214

## Summary
Severity: High
Advisory: BIT-postgresql-2021-23214
Aliases: CVE-2021-23214
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2021-23214
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=14.0.0 <14.0.1

## Details
When the server is configured to use trust authentication with a clientcert requirement or to use cert authentication, a man-in-the-middle attacker can inject arbitrary SQL queries when a connection is first established, despite the use of SSL certificate verification and encryption.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2022666
- https://git.postgresql.org/gitweb/?p=postgresql.git%3Ba=commit%3Bh=28e24125541545483093819efae9bca603441951
- https://github.com/postgres/postgres/commit/28e24125541545483093819efae9bca603441951
- https://security.gentoo.org/glsa/202211-04
- https://www.postgresql.org/support/security/CVE-2021-23214/
- https://nvd.nist.gov/vuln/detail/CVE-2021-23214
