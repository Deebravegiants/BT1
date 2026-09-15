# [H] ALPINE-CVE-2021-25215

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-25215
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-25215
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.11: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.12: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.13: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.14: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.15: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.16: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.17: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.18: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.19: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.20: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.21: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.22: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.23: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.24: `bind` — affected >=9.0.0 <9.16.15-r0

## Details
In BIND 9.0.0 -> 9.11.29, 9.12.0 -> 9.16.13, and versions BIND 9.9.3-S1 -> 9.11.29-S1 and 9.16.8-S1 -> 9.16.13-S1 of BIND Supported Preview Edition, as well as release versions 9.17.0 -> 9.17.11 of the BIND 9.17 development branch, when a vulnerable version of named receives a query for a record triggering the flaw described above, the named process will terminate due to a failed assertion check. The vulnerability affects all currently maintained BIND 9 branches (9.11, 9.11-S, 9.16, 9.16-S, 9.17) as well as all other versions of BIND 9.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-25215
