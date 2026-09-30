# [H] ALPINE-CVE-2017-17740

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-17740
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17740
Type: osv

## Affected
- Alpine:v3.10: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.11: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.12: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.13: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.14: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.15: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.16: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.17: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.18: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.19: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.20: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.21: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.22: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.23: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.24: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.7: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.8: `openldap` — affected >=0 <2.4.46-r0
- Alpine:v3.9: `openldap` — affected >=0 <2.4.46-r0

## Details
contrib/slapd-modules/nops/nops.c in OpenLDAP through 2.4.45, when both the nops module and the memberof overlay are enabled, attempts to free a buffer that was allocated on the stack, which allows remote attackers to cause a denial of service (slapd crash) via a member MODDN operation.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17740
