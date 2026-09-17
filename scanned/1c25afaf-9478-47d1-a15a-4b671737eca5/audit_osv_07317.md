# [H] BIT-postgresql-2022-2625

## Summary
Severity: High
Advisory: BIT-postgresql-2022-2625
Aliases: CVE-2022-2625
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2022-2625
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=14.0.0 <14.5.0

## Details
A vulnerability was found in PostgreSQL. This attack requires permission to create non-temporary objects in at least one schema, the ability to lure or wait for an administrator to create or update an affected extension in that schema, and the ability to lure or wait for a victim to use the object targeted in CREATE OR REPLACE or CREATE IF NOT EXISTS. Given all three prerequisites, this flaw allows an attacker to run arbitrary code as the victim role, which may be a superuser.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2113825
- https://security.gentoo.org/glsa/202211-04
- https://www.postgresql.org/about/news/postgresql-145-138-1212-1117-1022-and-15-beta-3-released-2496/
- https://nvd.nist.gov/vuln/detail/CVE-2022-2625
