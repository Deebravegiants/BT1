# [M] BIT-postgresql-2021-3393

## Summary
Severity: Medium
Advisory: BIT-postgresql-2021-3393
Aliases: CVE-2021-3393
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2021-3393
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=13.0.0 <13.2.0

## Details
An information leak was discovered in postgresql in versions before 13.2, before 12.6 and before 11.11. A user having UPDATE permission but not SELECT permission to a particular column could craft queries which, under some circumstances, might disclose values from that column in error messages. An attacker could use this flaw to obtain information stored in a column they are allowed to write but not read.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1924005
- https://security.gentoo.org/glsa/202105-32
- https://security.netapp.com/advisory/ntap-20210507-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2021-3393
