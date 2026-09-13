# [H] ALPINE-CVE-2019-19906

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-19906
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19906
Type: osv

## Affected
- Alpine:v3.10: `cyrus-sasl` — affected >=0 <2.1.27-r4
- Alpine:v3.11: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.12: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.13: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.14: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.15: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.16: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.17: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.18: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.19: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.20: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.21: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.22: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.23: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.24: `cyrus-sasl` — affected >=0 <2.1.27-r5
- Alpine:v3.8: `cyrus-sasl` — affected >=0 <2.1.26-r15
- Alpine:v3.9: `cyrus-sasl` — affected >=0 <2.1.27-r2

## Details
cyrus-sasl (aka Cyrus SASL) 2.1.27 has an out-of-bounds write leading to unauthenticated remote denial-of-service in OpenLDAP via a malformed LDAP packet. The OpenLDAP crash is ultimately caused by an off-by-one error in _sasl_add_string in common.c in cyrus-sasl.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19906
