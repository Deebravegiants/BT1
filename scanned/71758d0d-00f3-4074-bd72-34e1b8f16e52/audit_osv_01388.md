# [H] ALPINE-CVE-2019-13045

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-13045
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13045
Type: osv

## Affected
- Alpine:v3.10: `irssi` — affected >=0.8.18 <1.2.1-r0
- Alpine:v3.11: `irssi` — affected >=0.8.18 <1.2.1-r0
- Alpine:v3.12: `irssi` — affected >=0.8.18 <1.2.1-r0
- Alpine:v3.13: `irssi` — affected >=0.8.18 <1.2.1-r0
- Alpine:v3.14: `irssi` — affected >=0.8.18 <1.2.1-r0
- Alpine:v3.15: `irssi` — affected >=0.8.18 <1.2.1-r0
- Alpine:v3.16: `irssi` — affected >=0.8.18 <1.2.1-r0
- Alpine:v3.17: `irssi` — affected >=0.8.18 <1.2.1-r0
- Alpine:v3.7: `irssi` — affected >=0.8.18 <1.0.8-r0
- Alpine:v3.8: `irssi` — affected >=0.8.18 <1.1.3-r0
- Alpine:v3.9: `irssi` — affected >=0.8.18 <1.1.3-r0

## Details
Irssi before 1.0.8, 1.1.x before 1.1.3, and 1.2.x before 1.2.1, when SASL is enabled, has a use after free when sending SASL login to the server.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13045
