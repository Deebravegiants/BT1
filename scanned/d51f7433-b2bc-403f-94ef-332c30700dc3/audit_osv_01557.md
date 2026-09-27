# [H] ALPINE-CVE-2019-25016

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-25016
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-25016
Type: osv

## Affected
- Alpine:v3.11: `doas` — affected >=0 <6.6.1-r1
- Alpine:v3.12: `doas` — affected >=0 <6.6.1-r2
- Alpine:v3.13: `doas` — affected >=0 <6.8-r1
- Alpine:v3.14: `doas` — affected >=0 <6.8-r1
- Alpine:v3.15: `doas` — affected >=0 <6.8-r1
- Alpine:v3.16: `doas` — affected >=0 <6.8-r1
- Alpine:v3.17: `doas` — affected >=0 <6.8-r1
- Alpine:v3.18: `doas` — affected >=0 <6.8-r1
- Alpine:v3.19: `doas` — affected >=0 <6.8-r1
- Alpine:v3.20: `doas` — affected >=0 <6.8-r1
- Alpine:v3.21: `doas` — affected >=0 <6.8-r1
- Alpine:v3.22: `doas` — affected >=0 <6.8-r1
- Alpine:v3.23: `doas` — affected >=0 <6.8-r1
- Alpine:v3.24: `doas` — affected >=0 <6.8-r1

## Details
In OpenDoas from 6.6 to 6.8 the users PATH variable was incorrectly inherited by authenticated executions if the authenticating rule allowed the user to execute any command. Rules that only allowed to authenticated user to execute specific commands were not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-25016
