# [C] ALPINE-CVE-2021-31162

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-31162
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-31162
Type: osv

## Affected
- Alpine:v3.19: `rust` — affected >=1.48.0 <1.51.0-r2
- Alpine:v3.20: `rust` — affected >=1.48.0 <1.51.0-r2
- Alpine:v3.21: `rust` — affected >=1.48.0 <1.51.0-r2
- Alpine:v3.22: `rust` — affected >=1.48.0 <1.51.0-r2
- Alpine:v3.23: `rust` — affected >=1.48.0 <1.51.0-r2
- Alpine:v3.24: `rust` — affected >=1.48.0 <1.51.0-r2

## Details
In the standard library in Rust before 1.52.0, a double free can occur in the Vec::from_iter function if freeing the element panics.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-31162
