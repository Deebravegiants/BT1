# [H] ALPINE-CVE-2022-24407

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-24407
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24407
Type: osv

## Affected
- Alpine:v3.12: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.13: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.14: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.15: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.16: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.17: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.18: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.19: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.20: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.21: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.22: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.23: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0
- Alpine:v3.24: `cyrus-sasl` — affected >=2.1.17 <2.1.28-r0

## Details
In Cyrus SASL 2.1.17 through 2.1.27 before 2.1.28, plugins/sql.c does not escape the password for a SQL INSERT or UPDATE statement.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24407
