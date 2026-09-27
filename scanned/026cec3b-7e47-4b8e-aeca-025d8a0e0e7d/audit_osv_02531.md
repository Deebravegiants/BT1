# [H] ALPINE-CVE-2022-2881

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-2881
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2881
Type: osv

## Affected
- Alpine:v3.13: `bind` — affected >=9.18.0 <9.16.33-r0
- Alpine:v3.14: `bind` — affected >=9.18.0 <9.16.33-r0
- Alpine:v3.15: `bind` — affected >=9.18.0 <9.16.33-r0
- Alpine:v3.16: `bind` — affected >=9.18.0 <9.16.33-r0
- Alpine:v3.17: `bind` — affected >=9.18.0 <9.18.7-r0
- Alpine:v3.18: `bind` — affected >=9.18.0 <9.18.7-r0
- Alpine:v3.19: `bind` — affected >=9.18.0 <9.18.7-r0
- Alpine:v3.20: `bind` — affected >=9.18.0 <9.18.7-r0
- Alpine:v3.21: `bind` — affected >=9.18.0 <9.18.7-r0
- Alpine:v3.22: `bind` — affected >=9.18.0 <9.18.7-r0
- Alpine:v3.23: `bind` — affected >=9.18.0 <9.18.7-r0
- Alpine:v3.24: `bind` — affected >=9.18.0 <9.18.7-r0

## Details
The underlying bug might cause read past end of the buffer and either read memory it should not read, or crash the process.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2881
