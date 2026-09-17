# [M] ALPINE-CVE-2022-32213

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-32213
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-07-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-32213
Type: osv

## Affected
- Alpine:v3.13: `nodejs` — affected >=0 <14.20.1-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.20.1-r0
- Alpine:v3.15: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.16: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.17: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <16.17.1-r0

## Details
The llhttp parser <v14.20.1, <v16.17.1 and <v18.9.1 in the http module in Node.js does not correctly parse and validate Transfer-Encoding headers and can lead to HTTP Request Smuggling (HRS).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-32213
