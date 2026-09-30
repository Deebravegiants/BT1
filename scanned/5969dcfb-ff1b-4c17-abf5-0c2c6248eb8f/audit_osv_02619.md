# [H] ALPINE-CVE-2022-3736

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-3736
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3736
Type: osv

## Affected
- Alpine:v3.14: `bind` — affected >=9.16.12 <9.16.37-r0
- Alpine:v3.15: `bind` — affected >=9.16.12 <9.16.37-r0
- Alpine:v3.16: `bind` — affected >=9.16.12 <9.16.37-r0
- Alpine:v3.17: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.18: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.19: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.20: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.21: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.22: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.23: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.24: `bind` — affected >=9.16.12 <9.18.11-r0

## Details
BIND 9 resolver can crash when stale cache and stale answers are enabled, option `stale-answer-client-timeout` is set to a positive integer, and the resolver receives an RRSIG query.
This issue affects BIND 9 versions 9.16.12 through 9.16.36, 9.18.0 through 9.18.10, 9.19.0 through 9.19.8, and 9.16.12-S1 through 9.16.36-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3736
