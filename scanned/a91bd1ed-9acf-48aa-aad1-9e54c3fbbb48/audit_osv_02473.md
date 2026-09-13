# [M] ALPINE-CVE-2022-25313

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-25313
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-25313
Type: osv

## Affected
- Alpine:v3.12: `expat` — affected >=0 <2.2.10-r2
- Alpine:v3.13: `expat` — affected >=0 <2.2.10-r4
- Alpine:v3.14: `expat` — affected >=0 <2.4.5-r0
- Alpine:v3.15: `expat` — affected >=0 <2.4.5-r0
- Alpine:v3.16: `expat` — affected >=0 <2.4.5-r0
- Alpine:v3.17: `expat` — affected >=0 <2.4.5-r0
- Alpine:v3.18: `expat` — affected >=0 <2.4.5-r0
- Alpine:v3.19: `expat` — affected >=0 <2.4.5-r0
- Alpine:v3.20: `expat` — affected >=0 <2.4.5-r0
- Alpine:v3.21: `expat` — affected >=0 <2.4.5-r0
- Alpine:v3.22: `expat` — affected >=0 <2.4.5-r0
- Alpine:v3.23: `expat` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `expat` — affected >=0 <2.4.5-r0

## Details
In Expat (aka libexpat) before 2.4.5, an attacker can trigger stack exhaustion in build_model via a large nesting depth in the DTD element.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-25313
