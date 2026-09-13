# [M] BIT-postgresql-2021-20229

## Summary
Severity: Medium
Advisory: BIT-postgresql-2021-20229
Aliases: CVE-2021-20229
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2021-20229
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=13.0.0 <13.2.0

## Details
A flaw was found in PostgreSQL in versions before 13.2. This flaw allows a user with SELECT privilege on one column to craft a special query that returns all columns of the table. The highest threat from this vulnerability is to confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1925296
- https://security.gentoo.org/glsa/202105-32
- https://security.netapp.com/advisory/ntap-20210326-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2021-20229
