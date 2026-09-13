# [M] ALPINE-CVE-2017-14159

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-14159
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14159
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
slapd in OpenLDAP 2.4.45 and earlier creates a PID file after dropping privileges to a non-root account, which might allow local users to kill arbitrary processes by leveraging access to this non-root account for PID file modification before a root script executes a "kill `cat /pathname`" command, as demonstrated by openldap-initscript.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14159
