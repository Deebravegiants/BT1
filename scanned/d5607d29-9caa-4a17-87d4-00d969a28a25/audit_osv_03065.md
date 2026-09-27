# [M] ALPINE-CVE-2024-36357

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-36357
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-36357
Type: osv

## Affected
- Alpine:v3.19: `xen` — affected >=0 <4.18.5-r1
- Alpine:v3.20: `xen` — affected >=0 <4.18.5-r1
- Alpine:v3.21: `xen` — affected >=0 <4.19.2-r2
- Alpine:v3.22: `xen` — affected >=0 <4.20.1-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.1-r0
- Alpine:v3.24: `xen` — affected >=0 <4.20.1-r0

## Details
A transient execution vulnerability in some AMD processors may allow an attacker to infer data in the L1D cache, potentially resulting in the leakage of sensitive information across privileged boundaries.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-36357
