# [H] ALPINE-CVE-2024-7592

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-7592
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-7592
Type: osv

## Affected
- Alpine:v3.17: `python3` — affected >=0 <3.10.15-r0
- Alpine:v3.18: `python3` — affected >=0 <3.11.10-r0
- Alpine:v3.19: `python3` — affected >=0 <3.11.10-r0
- Alpine:v3.20: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.21: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.24: `python3` — affected >=0 <3.12.6-r0

## Details
There is a LOW severity vulnerability affecting CPython, specifically the
'http.cookies' standard library module.


When parsing cookies that contained backslashes for quoted characters in
the cookie value, the parser would use an algorithm with quadratic
complexity, resulting in excess CPU resources being used while parsing the
value.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-7592
