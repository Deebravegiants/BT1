# [M] ALPINE-CVE-2019-13057

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-13057
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13057
Type: osv

## Affected
- Alpine:v3.10: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.11: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.12: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.13: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.14: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.15: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.16: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.17: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.18: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.19: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.20: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.21: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.22: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.23: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.24: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.7: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.8: `openldap` — affected >=0 <2.4.48-r0
- Alpine:v3.9: `openldap` — affected >=0 <2.4.48-r0

## Details
An issue was discovered in the server in OpenLDAP before 2.4.48. When the server administrator delegates rootDN (database admin) privileges for certain databases but wants to maintain isolation (e.g., for multi-tenant deployments), slapd does not properly stop a rootDN from requesting authorization as an identity from another database during a SASL bind or with a proxyAuthz (RFC 4370) control. (It is not a common configuration to deploy a system where the server administrator and a DB administrator enjoy different levels of trust.)

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13057
