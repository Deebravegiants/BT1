# [H] ALPINE-CVE-2024-6232

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-6232
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-6232
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
There is a MEDIUM severity vulnerability affecting CPython.





Regular expressions that allowed excessive backtracking during tarfile.TarFile header parsing are vulnerable to ReDoS via specifically-crafted tar archives.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-6232
