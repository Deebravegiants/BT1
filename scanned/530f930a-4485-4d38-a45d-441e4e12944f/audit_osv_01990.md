# [H] ALPINE-CVE-2020-36323

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-36323
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-36323
Type: osv

## Affected
- Alpine:v3.19: `rust` — affected >=0 <1.51.0-r2
- Alpine:v3.20: `rust` — affected >=0 <1.51.0-r2
- Alpine:v3.21: `rust` — affected >=0 <1.51.0-r2
- Alpine:v3.22: `rust` — affected >=0 <1.51.0-r2
- Alpine:v3.23: `rust` — affected >=0 <1.51.0-r2
- Alpine:v3.24: `rust` — affected >=0 <1.51.0-r2

## Details
In the standard library in Rust before 1.52.0, there is an optimization for joining strings that can cause uninitialized bytes to be exposed (or the program to crash) if the borrowed string changes after its length is checked.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-36323
