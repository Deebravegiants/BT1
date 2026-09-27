# [M] ALPINE-CVE-2021-37750

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-37750
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-37750
Type: osv

## Affected
- Alpine:v3.12: `krb5` — affected >=0 <1.18.5-r0
- Alpine:v3.13: `krb5` — affected >=0 <1.18.5-r0
- Alpine:v3.14: `krb5` — affected >=0 <1.18.5-r0
- Alpine:v3.15: `krb5` — affected >=0 <1.19.3-r0
- Alpine:v3.16: `krb5` — affected >=0 <1.19.3-r0
- Alpine:v3.17: `krb5` — affected >=0 <1.19.3-r0
- Alpine:v3.18: `krb5` — affected >=0 <1.19.3-r0
- Alpine:v3.19: `krb5` — affected >=0 <1.19.3-r0
- Alpine:v3.20: `krb5` — affected >=0 <1.19.3-r0
- Alpine:v3.21: `krb5` — affected >=0 <1.19.3-r0
- Alpine:v3.22: `krb5` — affected >=0 <1.19.3-r0
- Alpine:v3.23: `krb5` — affected >=0 <1.19.3-r0
- Alpine:v3.24: `krb5` — affected >=0 <1.19.3-r0

## Details
The Key Distribution Center (KDC) in MIT Kerberos 5 (aka krb5) before 1.18.5 and 1.19.x before 1.19.3 has a NULL pointer dereference in kdc/do_tgs_req.c via a FAST inner body that lacks a server field.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-37750
