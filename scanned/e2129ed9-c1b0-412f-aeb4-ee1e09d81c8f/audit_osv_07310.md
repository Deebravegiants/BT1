# [H] BIT-postgresql-2021-32027

## Summary
Severity: High
Advisory: BIT-postgresql-2021-32027
Aliases: CVE-2021-32027
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2021-32027
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=13.0.0 <13.3.0

## Details
A flaw was found in postgresql in versions before 13.3, before 12.7, before 11.12, before 10.17 and before 9.6.22. While modifying certain SQL array values, missing bounds checks let authenticated database users write arbitrary bytes to a wide area of server memory. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1956876
- https://security.gentoo.org/glsa/202211-04
- https://security.netapp.com/advisory/ntap-20210713-0004/
- https://www.postgresql.org/support/security/CVE-2021-32027/
- https://nvd.nist.gov/vuln/detail/CVE-2021-32027
