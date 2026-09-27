# [C] ALPINE-CVE-2022-29155

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-29155
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-29155
Type: osv

## Affected
- Alpine:v3.15: `openldap` — affected >=2.0 <2.6.2-r0
- Alpine:v3.16: `openldap` — affected >=2.0 <2.6.2-r0
- Alpine:v3.17: `openldap` — affected >=2.0 <2.6.2-r0
- Alpine:v3.18: `openldap` — affected >=2.0 <2.6.2-r0
- Alpine:v3.19: `openldap` — affected >=2.0 <2.6.2-r0
- Alpine:v3.20: `openldap` — affected >=2.0 <2.6.2-r0
- Alpine:v3.21: `openldap` — affected >=2.0 <2.6.2-r0
- Alpine:v3.22: `openldap` — affected >=2.0 <2.6.2-r0
- Alpine:v3.23: `openldap` — affected >=2.0 <2.6.2-r0
- Alpine:v3.24: `openldap` — affected >=2.0 <2.6.2-r0

## Details
In OpenLDAP 2.x before 2.5.12 and 2.6.x before 2.6.2, a SQL injection vulnerability exists in the experimental back-sql backend to slapd, via a SQL statement within an LDAP query. This can occur during an LDAP search operation when the search filter is processed, due to a lack of proper escaping.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-29155
