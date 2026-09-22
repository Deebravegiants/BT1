# [H] ALPINE-CVE-2017-14919

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14919
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14919
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.11: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.12: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.13: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.14: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.15: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.16: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.17: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.18: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.19: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.20: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.21: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.22: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.23: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.24: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.7: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.8: `nodejs` — affected >=0 <6.11.5-r0
- Alpine:v3.9: `nodejs` — affected >=0 <6.11.5-r0

## Details
Node.js before 4.8.5, 6.x before 6.11.5, and 8.x before 8.8.0 allows remote attackers to cause a denial of service (uncaught exception and crash) by leveraging a change in the zlib module 1.2.9 making 8 an invalid value for the windowBits parameter.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14919
