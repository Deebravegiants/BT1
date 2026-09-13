# [M] ALPINE-CVE-2022-21123

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-21123
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-06-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-21123
Type: osv

## Affected
- Alpine:v3.13: `xen` — affected >=0 <4.14.5-r2
- Alpine:v3.14: `xen` — affected >=0 <4.15.2-r2
- Alpine:v3.15: `xen` — affected >=0 <4.15.2-r2
- Alpine:v3.16: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.17: `xen` — affected >=0 <4.16.1-r3
- Alpine:v3.18: `xen` — affected >=0 <4.16.1-r3
- Alpine:v3.19: `xen` — affected >=0 <4.16.1-r3
- Alpine:v3.20: `xen` — affected >=0 <4.16.1-r3
- Alpine:v3.21: `xen` — affected >=0 <4.16.1-r3
- Alpine:v3.22: `xen` — affected >=0 <4.16.1-r3
- Alpine:v3.23: `xen` — affected >=0 <4.16.1-r3
- Alpine:v3.24: `xen` — affected >=0 <4.16.1-r3

## Details
Incomplete cleanup of multi-core shared buffers for some Intel(R) Processors may allow an authenticated user to potentially enable information disclosure via local access.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-21123
