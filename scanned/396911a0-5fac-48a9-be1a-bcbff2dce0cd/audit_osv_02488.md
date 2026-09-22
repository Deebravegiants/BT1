# [C] ALPINE-CVE-2022-26651

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-26651
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-26651
Type: osv

## Affected
- Alpine:v3.15: `asterisk` — affected >=16.0.0 <18.2.2-r6
- Alpine:v3.16: `asterisk` — affected >=16.0.0 <18.11.2-r0
- Alpine:v3.17: `asterisk` — affected >=16.0.0 <18.11.2-r0
- Alpine:v3.18: `asterisk` — affected >=16.0.0 <18.11.2-r0
- Alpine:v3.19: `asterisk` — affected >=16.0.0 <18.11.2-r0
- Alpine:v3.20: `asterisk` — affected >=16.0.0 <18.11.2-r0
- Alpine:v3.21: `asterisk` — affected >=16.0.0 <18.11.2-r0
- Alpine:v3.22: `asterisk` — affected >=16.0.0 <18.11.2-r0
- Alpine:v3.23: `asterisk` — affected >=16.0.0 <18.11.2-r0
- Alpine:v3.24: `asterisk` — affected >=16.0.0 <18.11.2-r0

## Details
An issue was discovered in Asterisk through 19.x and Certified Asterisk through 16.8-cert13. The func_odbc module provides possibly inadequate escaping functionality for backslash characters in SQL queries, resulting in user-provided data creating a broken SQL query or possibly a SQL injection. This is fixed in 16.25.2, 18.11.2, and 19.3.2, and 16.8-cert14.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-26651
