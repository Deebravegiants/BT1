# [H] ALPINE-CVE-2023-47038

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-47038
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-47038
Type: osv

## Affected
- Alpine:v3.15: `perl` — affected >=5.30.0 <5.34.2-r0
- Alpine:v3.16: `perl` — affected >=5.30.0 <5.34.2-r0
- Alpine:v3.17: `perl` — affected >=5.30.0 <5.36.2-r0
- Alpine:v3.18: `perl` — affected >=5.30.0 <5.36.2-r0
- Alpine:v3.19: `perl` — affected >=5.30.0 <5.38.1-r0
- Alpine:v3.20: `perl` — affected >=5.30.0 <5.38.1-r0
- Alpine:v3.21: `perl` — affected >=5.30.0 <5.38.1-r0
- Alpine:v3.22: `perl` — affected >=5.30.0 <5.38.1-r0
- Alpine:v3.23: `perl` — affected >=5.30.0 <5.38.1-r0
- Alpine:v3.24: `perl` — affected >=5.30.0 <5.38.1-r0

## Details
A vulnerability was found in perl 5.30.0 through 5.38.0. This issue occurs when a crafted regular expression is compiled by perl, which can allow an attacker controlled byte buffer overflow in a heap allocated buffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-47038
