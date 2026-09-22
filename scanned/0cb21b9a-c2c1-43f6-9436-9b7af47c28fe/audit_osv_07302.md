# [M] BIT-postgresql-2020-1720

## Summary
Severity: Medium
Advisory: BIT-postgresql-2020-1720
Aliases: CVE-2020-1720
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2020-1720
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=12.0.0 <12.2.0

## Details
A flaw was found in PostgreSQL's "ALTER ... DEPENDS ON EXTENSION", where sub-commands did not perform authorization checks. An authenticated attacker could use this flaw in certain configurations to perform drop objects such as function, triggers, et al., leading to database corruption. This issue affects PostgreSQL versions before 12.2, before 11.7, before 10.12 and before 9.6.17.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00043.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1720
- https://www.postgresql.org/about/news/2011/
- https://nvd.nist.gov/vuln/detail/CVE-2020-1720
