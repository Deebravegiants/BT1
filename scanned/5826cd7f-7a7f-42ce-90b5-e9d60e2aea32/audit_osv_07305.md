# [H] BIT-postgresql-2020-25695

## Summary
Severity: High
Advisory: BIT-postgresql-2020-25695
Aliases: CVE-2020-25695
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2020-25695
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=13.0.0 <13.1.0

## Details
A flaw was found in PostgreSQL versions before 13.1, before 12.5, before 11.10, before 10.15, before 9.6.20 and before 9.5.24. An attacker having permission to create non-temporary objects in at least one schema can execute arbitrary SQL functions under the identity of a superuser. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1894425
- https://lists.debian.org/debian-lts-announce/2020/12/msg00005.html
- https://security.gentoo.org/glsa/202012-07
- https://security.netapp.com/advisory/ntap-20201202-0003/
- https://www.postgresql.org/support/security/
- https://nvd.nist.gov/vuln/detail/CVE-2020-25695
