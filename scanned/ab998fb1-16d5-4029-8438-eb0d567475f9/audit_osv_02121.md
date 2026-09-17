# [M] ALPINE-CVE-2021-25220

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-25220
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-25220
Type: osv

## Affected
- Alpine:v3.12: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.13: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.14: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.15: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.16: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.17: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.18: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.19: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.20: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.21: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.22: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.23: `bind` — affected >=9.11.0 <9.16.27-r0
- Alpine:v3.24: `bind` — affected >=9.11.0 <9.16.27-r0

## Details
BIND 9.11.0 -> 9.11.36 9.12.0 -> 9.16.26 9.17.0 -> 9.18.0 BIND Supported Preview Editions: 9.11.4-S1 -> 9.11.36-S1 9.16.8-S1 -> 9.16.26-S1 Versions of BIND 9 earlier than those shown - back to 9.1.0, including Supported Preview Editions - are also believed to be affected but have not been tested as they are EOL. The cache could become poisoned with incorrect records leading to queries being made to the wrong servers, which might also result in false information being returned to clients.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-25220
