# [H] ALPINE-CVE-2020-36226

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-36226
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-36226
Type: osv

## Affected
- Alpine:v3.13: `openldap` — affected >=0 <2.4.57-r0
- Alpine:v3.14: `openldap` — affected >=0 <2.4.57-r0
- Alpine:v3.15: `openldap` — affected >=0 <2.4.57-r0
- Alpine:v3.16: `openldap` — affected >=0 <2.4.57-r0
- Alpine:v3.17: `openldap` — affected >=0 <2.4.57-r0
- Alpine:v3.18: `openldap` — affected >=0 <2.4.57-r0
- Alpine:v3.19: `openldap` — affected >=0 <2.4.57-r0
- Alpine:v3.20: `openldap` — affected >=0 <2.4.57-r0
- Alpine:v3.21: `openldap` — affected >=0 <2.4.57-r0
- Alpine:v3.22: `openldap` — affected >=0 <2.4.57-r0
- Alpine:v3.23: `openldap` — affected >=0 <2.4.57-r0
- Alpine:v3.24: `openldap` — affected >=0 <2.4.57-r0

## Details
A flaw was discovered in OpenLDAP before 2.4.57 leading to a memch->bv_len miscalculation and slapd crash in the saslAuthzTo processing, resulting in denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-36226
