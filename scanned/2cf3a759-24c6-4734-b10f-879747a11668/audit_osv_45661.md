# [C] JLSEC-2026-174

## Summary
Severity: Critical
Advisory: JLSEC-2026-174
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/JLSEC-2026-174
Type: osv

## Affected
- Julia: `OpenLDAPClient_jll` — affected >=0 <2.5.14+0

## Details
In OpenLDAP 2.x before 2.5.12 and 2.6.x before 2.6.2, a SQL injection vulnerability exists in the experimental back-sql backend to slapd, via a SQL statement within an LDAP query. This can occur during an LDAP search operation when the search filter is processed, due to a lack of proper escaping.

## References
- https://bugs.openldap.org/show_bug.cgi?id=9815
- https://lists.debian.org/debian-lts-announce/2022/05/msg00032.html
- https://security.netapp.com/advisory/ntap-20220609-0007/
- https://www.debian.org/security/2022/dsa-5140
