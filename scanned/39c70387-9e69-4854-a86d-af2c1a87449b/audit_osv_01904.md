# [H] ALPINE-CVE-2020-25709

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25709
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25709
Type: osv

## Affected
- Alpine:v3.10: `openldap` — affected >=0 <2.4.48-r2
- Alpine:v3.11: `openldap` — affected >=0 <2.4.48-r3
- Alpine:v3.12: `openldap` — affected >=0 <2.4.50-r1
- Alpine:v3.13: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.14: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.15: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.16: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.17: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.18: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.19: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.20: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.21: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.22: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.23: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.24: `openldap` — affected >=0 <2.4.56-r0
- Alpine:v3.9: `openldap` — affected >=0 <2.4.48-r2

## Details
A flaw was found in OpenLDAP. This flaw allows an attacker who can send a malicious packet to be processed by OpenLDAP’s slapd server, to trigger an assertion failure. The highest threat from this vulnerability is to system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25709
