# [M] ALPINE-CVE-2018-20217

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-20217
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20217
Type: osv

## Affected
- Alpine:v3.10: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.11: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.12: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.13: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.14: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.15: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.16: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.17: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.18: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.19: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.20: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.21: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.22: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.23: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.24: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.6: `krb5` — affected >=0 <1.14.3-r3
- Alpine:v3.7: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.8: `krb5` — affected >=0 <1.15.4-r0
- Alpine:v3.9: `krb5` — affected >=0 <1.15.4-r0

## Details
A Reachable Assertion issue was discovered in the KDC in MIT Kerberos 5 (aka krb5) before 1.17. If an attacker can obtain a krbtgt ticket using an older encryption type (single-DES, triple-DES, or RC4), the attacker can crash the KDC by making an S4U2Self request.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20217
