# [M] ALPINE-CVE-2022-35256

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-35256
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-35256
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
The llhttp parser in the http module in Node v18.7.0 does not correctly handle header fields that are not terminated with CLRF. This may result in HTTP Request Smuggling.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-35256
