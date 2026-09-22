# [H] ALPINE-CVE-2021-36222

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-36222
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-36222
Type: osv

## Affected
- Alpine:v3.12: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.13: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.14: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.15: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.16: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.17: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.18: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.19: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.20: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.21: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.22: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.23: `krb5` — affected >=0 <1.18.4-r0
- Alpine:v3.24: `krb5` — affected >=0 <1.18.4-r0

## Details
ec_verify in kdc/kdc_preauth_ec.c in the Key Distribution Center (KDC) in MIT Kerberos 5 (aka krb5) before 1.18.4 and 1.19.x before 1.19.2 allows remote attackers to cause a NULL pointer dereference and daemon crash. This occurs because a return value is not properly managed in a certain situation.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-36222
