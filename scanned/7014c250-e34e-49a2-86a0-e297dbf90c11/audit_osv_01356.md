# [H] ALPINE-CVE-2019-11922

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-11922
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11922
Type: osv

## Affected
- Alpine:v3.11: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.12: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.13: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.14: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.15: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.16: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.17: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.18: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.19: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.20: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.21: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.22: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.23: `zstd` — affected >=0 <1.3.8-r0
- Alpine:v3.24: `zstd` — affected >=0 <1.3.8-r0

## Details
A race condition in the one-pass compression functions of Zstandard prior to version 1.3.8 could allow an attacker to write bytes out of bounds if an output buffer smaller than the recommended size was used.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11922
