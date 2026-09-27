# [H] ALPINE-CVE-2021-42771

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-42771
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-42771
Type: osv

## Affected
- Alpine:v3.16: `py3-babel` — affected >=0 <2.9.1-r0
- Alpine:v3.17: `py3-babel` — affected >=0 <2.9.1-r0
- Alpine:v3.18: `py3-babel` — affected >=0 <2.9.1-r0
- Alpine:v3.19: `py3-babel` — affected >=0 <2.9.1-r0
- Alpine:v3.20: `py3-babel` — affected >=0 <2.9.1-r0
- Alpine:v3.21: `py3-babel` — affected >=0 <2.9.1-r0
- Alpine:v3.22: `py3-babel` — affected >=0 <2.9.1-r0
- Alpine:v3.23: `py3-babel` — affected >=0 <2.9.1-r0
- Alpine:v3.24: `py3-babel` — affected >=0 <2.9.1-r0

## Details
Babel.Locale in Babel before 2.9.1 allows attackers to load arbitrary locale .dat files (containing serialized Python objects) via directory traversal, leading to code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-42771
