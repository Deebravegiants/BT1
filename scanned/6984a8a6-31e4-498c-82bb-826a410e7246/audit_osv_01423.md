# [H] ALPINE-CVE-2019-13565

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-13565
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13565
Type: osv

## Affected
- Alpine:v3.10: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.11: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.12: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.13: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.14: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.15: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.16: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.17: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.18: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.19: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.20: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.21: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.22: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.23: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.24: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.7: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.8: `openldap` — affected >=2.0 <2.4.48-r0
- Alpine:v3.9: `openldap` — affected >=2.0 <2.4.48-r0

## Details
An issue was discovered in OpenLDAP 2.x before 2.4.48. When using SASL authentication and session encryption, and relying on the SASL security layers in slapd access controls, it is possible to obtain access that would otherwise be denied via a simple bind for any identity covered in those ACLs. After the first SASL bind is completed, the sasl_ssf value is retained for all new non-SASL connections. Depending on the ACL configuration, this can affect different types of operations (searches, modifications, etc.). In other words, a successful authorization step completed by one user affects the authorization requirement for a different user.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13565
