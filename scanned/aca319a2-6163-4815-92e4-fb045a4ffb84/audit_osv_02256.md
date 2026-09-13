# [H] ALPINE-CVE-2021-36367

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-36367
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2021-07-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-36367
Type: osv

## Affected
- Alpine:v3.11: `putty` — affected >=0 <0.76-r0
- Alpine:v3.12: `putty` — affected >=0 <0.76-r0
- Alpine:v3.13: `putty` — affected >=0 <0.76-r0
- Alpine:v3.14: `putty` — affected >=0 <0.76-r0
- Alpine:v3.15: `putty` — affected >=0 <0.76-r0
- Alpine:v3.16: `putty` — affected >=0 <0.76-r0
- Alpine:v3.17: `putty` — affected >=0 <0.76-r0
- Alpine:v3.18: `putty` — affected >=0 <0.76-r0
- Alpine:v3.19: `putty` — affected >=0 <0.76-r0

## Details
PuTTY through 0.75 proceeds with establishing an SSH session even if it has never sent a substantive authentication response. This makes it easier for an attacker-controlled SSH server to present a later spoofed authentication prompt (that the attacker can use to capture credential data, and use that data for purposes that are undesired by the client user).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-36367
