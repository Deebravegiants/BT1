# [H] ALPINE-CVE-2021-20214

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-20214
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20214
Type: osv

## Affected
- Alpine:v3.12: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.13: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.14: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.15: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.16: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.17: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.18: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.19: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.20: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.21: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.22: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.23: `privoxy` — affected >=0 <3.0.29-r0
- Alpine:v3.24: `privoxy` — affected >=0 <3.0.29-r0

## Details
A flaw was found in Privoxy in versions before 3.0.29. Memory leaks in the client-tags CGI handler when client tags are configured and memory allocations fail can lead to a system crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20214
