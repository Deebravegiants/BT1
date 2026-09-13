# [H] ALPINE-CVE-2026-25210

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-25210
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-25210
Type: osv

## Affected
- Alpine:v3.20: `expat` — affected >=0 <2.7.4-r0
- Alpine:v3.21: `expat` — affected >=0 <2.7.4-r0
- Alpine:v3.22: `expat` — affected >=0 <2.7.4-r0
- Alpine:v3.23: `expat` — affected >=0 <2.7.4-r0
- Alpine:v3.24: `expat` — affected >=0 <2.7.4-r0

## Details
In libexpat before 2.7.4, the doContent function does not properly determine the buffer size bufSize because there is no integer overflow check for tag buffer reallocation.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-25210
