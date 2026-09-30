# [M] ALPINE-CVE-2018-5710

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-5710
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5710
Type: osv

## Affected
- Alpine:v3.10: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.11: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.12: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.13: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.14: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.15: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.16: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.17: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.18: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.19: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.20: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.21: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.22: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.23: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.24: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.7: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.8: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.9: `krb5` — affected >=0 <1.15.3-r0

## Details
An issue was discovered in MIT Kerberos 5 (aka krb5) through 1.16. The pre-defined function "strlen" is getting a "NULL" string as a parameter value in plugins/kdb/ldap/libkdb_ldap/ldap_principal2.c in the Key Distribution Center (KDC), which allows remote authenticated users to cause a denial of service (NULL pointer dereference) via a modified kadmin client.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5710
