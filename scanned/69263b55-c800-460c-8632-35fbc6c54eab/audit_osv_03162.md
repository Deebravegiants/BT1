# [M] ALPINE-CVE-2024-6923

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-6923
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-08-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-6923
Type: osv

## Affected
- Alpine:v3.17: `python3` — affected >=0 <3.10.15-r0
- Alpine:v3.18: `python3` — affected >=0 <3.11.10-r0
- Alpine:v3.19: `python3` — affected >=0 <3.11.10-r0
- Alpine:v3.20: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.21: `python3` — affected >=0 <3.12.5-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.5-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.5-r0
- Alpine:v3.24: `python3` — affected >=0 <3.12.5-r0

## Details
There is a MEDIUM severity vulnerability affecting CPython.

The 
email module didn’t properly quote newlines for email headers when 
serializing an email message allowing for header injection when an email
 is serialized.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-6923
