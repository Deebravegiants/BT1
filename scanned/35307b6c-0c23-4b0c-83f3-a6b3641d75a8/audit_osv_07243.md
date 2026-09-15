# [C] BIT-openldap-2022-29155

## Summary
Severity: Critical
Advisory: BIT-openldap-2022-29155
Aliases: CVE-2022-29155
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-openldap-2022-29155
Type: osv

## Affected
- Bitnami: `openldap` — affected >=2.6.0 <2.6.2

## Details
In OpenLDAP 2.x before 2.5.12 and 2.6.x before 2.6.2, a SQL injection vulnerability exists in the experimental back-sql backend to slapd, via a SQL statement within an LDAP query. This can occur during an LDAP search operation when the search filter is processed, due to a lack of proper escaping.

## References
- https://bugs.openldap.org/show_bug.cgi?id=9815
- https://lists.debian.org/debian-lts-announce/2022/05/msg00032.html
- https://security.netapp.com/advisory/ntap-20220609-0007/
- https://www.debian.org/security/2022/dsa-5140
- https://nvd.nist.gov/vuln/detail/CVE-2022-29155
