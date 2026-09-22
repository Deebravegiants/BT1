# [H] ALPINE-CVE-2020-28196

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-28196
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-28196
Type: osv

## Affected
- Alpine:v3.10: `krb5` — affected >=0 <1.17.2-r0
- Alpine:v3.11: `krb5` — affected >=0 <1.17.2-r0
- Alpine:v3.12: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.13: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.14: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.15: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.16: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.17: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.18: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.19: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.20: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.21: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.22: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.23: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.24: `krb5` — affected >=0 <1.18.3-r0
- Alpine:v3.9: `krb5` — affected >=0 <1.15.5-r1

## Details
MIT Kerberos 5 (aka krb5) before 1.17.2 and 1.18.x before 1.18.3 allows unbounded recursion via an ASN.1-encoded Kerberos message because the lib/krb5/asn.1/asn1_encode.c support for BER indefinite lengths lacks a recursion limit.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-28196
