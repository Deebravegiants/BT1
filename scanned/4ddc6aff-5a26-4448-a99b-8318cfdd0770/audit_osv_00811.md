# [M] ALPINE-CVE-2017-9287

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-9287
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9287
Type: osv

## Affected
- Alpine:v3.10: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.11: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.12: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.13: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.14: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.15: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.16: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.17: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.18: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.19: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.20: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.21: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.22: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.23: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.24: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.3: `openldap` — affected >=0 <2.4.44-r1
- Alpine:v3.4: `openldap` — affected >=0 <2.4.44-r2
- Alpine:v3.5: `openldap` — affected >=0 <2.4.44-r4
- Alpine:v3.6: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.7: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.8: `openldap` — affected >=0 <2.4.44-r5
- Alpine:v3.9: `openldap` — affected >=0 <2.4.44-r5

## Details
servers/slapd/back-mdb/search.c in OpenLDAP through 2.4.44 is prone to a double free vulnerability. A user with access to search the directory can crash slapd by issuing a search including the Paged Results control with a page size of 0.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9287
