# [M] BIT-postgresql-2021-32029

## Summary
Severity: Medium
Advisory: BIT-postgresql-2021-32029
Aliases: CVE-2021-32029
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2021-32029
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=13.0.0 <13.3.0

## Details
A flaw was found in postgresql. Using an UPDATE ... RETURNING command on a purpose-crafted table, an authenticated database user could read arbitrary bytes of server memory. The highest threat from this vulnerability is to data confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1956883
- https://security.netapp.com/advisory/ntap-20211112-0003/
- https://www.postgresql.org/support/security/CVE-2021-32029/
- https://nvd.nist.gov/vuln/detail/CVE-2021-32029
