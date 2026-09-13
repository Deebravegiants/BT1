# [H] ALPINE-CVE-2021-23017

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-23017
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-23017
Type: osv

## Affected
- Alpine:v3.10: `nginx` — affected >=0.6.18 <1.16.1-r3
- Alpine:v3.11: `nginx` — affected >=0.6.18 <1.16.1-r7
- Alpine:v3.12: `nginx` — affected >=0.6.18 <1.18.0-r2
- Alpine:v3.13: `nginx` — affected >=0.6.18 <1.18.0-r14
- Alpine:v3.14: `nginx` — affected >=0.6.18 <1.20.1-r0
- Alpine:v3.15: `nginx` — affected >=0.6.18 <1.20.1-r0
- Alpine:v3.16: `nginx` — affected >=0.6.18 <1.20.1-r0
- Alpine:v3.17: `nginx` — affected >=0.6.18 <1.20.1-r0
- Alpine:v3.18: `nginx` — affected >=0.6.18 <1.20.1-r0
- Alpine:v3.19: `nginx` — affected >=0.6.18 <1.20.1-r0
- Alpine:v3.20: `nginx` — affected >=0.6.18 <1.20.1-r0
- Alpine:v3.21: `nginx` — affected >=0.6.18 <1.20.1-r0
- Alpine:v3.22: `nginx` — affected >=0.6.18 <1.20.1-r0
- Alpine:v3.23: `nginx` — affected >=0.6.18 <1.20.1-r0
- Alpine:v3.24: `nginx` — affected >=0.6.18 <1.20.1-r0

## Details
A security issue in nginx resolver was identified, which might allow an attacker who is able to forge UDP packets from the DNS server to cause 1-byte memory overwrite, resulting in worker process crash or potential other impact.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-23017
