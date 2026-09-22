# [M] ALPINE-CVE-2021-3426

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3426
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3426
Type: osv

## Affected
- Alpine:v3.15: `python3` — affected >=0 <3.9.4-r0
- Alpine:v3.16: `python3` — affected >=0 <3.9.4-r0
- Alpine:v3.17: `python3` — affected >=0 <3.9.4-r0
- Alpine:v3.18: `python3` — affected >=0 <3.9.4-r0
- Alpine:v3.19: `python3` — affected >=0 <3.9.4-r0
- Alpine:v3.20: `python3` — affected >=0 <3.9.4-r0
- Alpine:v3.21: `python3` — affected >=0 <3.9.4-r0
- Alpine:v3.22: `python3` — affected >=0 <3.9.4-r0
- Alpine:v3.23: `python3` — affected >=0 <3.9.4-r0
- Alpine:v3.24: `python3` — affected >=0 <3.9.4-r0

## Details
There's a flaw in Python 3's pydoc. A local or adjacent attacker who discovers or is able to convince another local or adjacent user to start a pydoc server could access the server and use it to disclose sensitive information belonging to the other user that they would not normally be able to access. The highest risk of this flaw is to data confidentiality. This flaw affects Python versions before 3.8.9, Python versions before 3.9.3 and Python versions before 3.10.0a7.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3426
