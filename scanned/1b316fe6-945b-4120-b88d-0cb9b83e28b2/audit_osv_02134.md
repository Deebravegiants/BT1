# [H] ALPINE-CVE-2021-27212

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-27212
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-27212
Type: osv

## Affected
- Alpine:v3.12: `openldap` — affected >=0 <2.4.50-r2
- Alpine:v3.13: `openldap` — affected >=0 <2.4.57-r1
- Alpine:v3.14: `openldap` — affected >=0 <2.4.57-r1
- Alpine:v3.15: `openldap` — affected >=0 <2.4.57-r1
- Alpine:v3.16: `openldap` — affected >=0 <2.4.57-r1
- Alpine:v3.17: `openldap` — affected >=0 <2.4.57-r1
- Alpine:v3.18: `openldap` — affected >=0 <2.4.57-r1
- Alpine:v3.19: `openldap` — affected >=0 <2.4.57-r1
- Alpine:v3.20: `openldap` — affected >=0 <2.4.57-r1
- Alpine:v3.21: `openldap` — affected >=0 <2.4.57-r1
- Alpine:v3.22: `openldap` — affected >=0 <2.4.57-r1
- Alpine:v3.23: `openldap` — affected >=0 <2.4.57-r1
- Alpine:v3.24: `openldap` — affected >=0 <2.4.57-r1

## Details
In OpenLDAP through 2.4.57 and 2.5.x through 2.5.1alpha, an assertion failure in slapd can occur in the issuerAndThisUpdateCheck function via a crafted packet, resulting in a denial of service (daemon exit) via a short timestamp. This is related to schema_init.c and checkTime.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-27212
