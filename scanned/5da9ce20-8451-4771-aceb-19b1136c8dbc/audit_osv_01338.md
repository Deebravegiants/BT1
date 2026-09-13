# [M] ALPINE-CVE-2019-11135

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-11135
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2019-11-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11135
Type: osv

## Affected
- Alpine:v3.13: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.14: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.15: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.16: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.17: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.18: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.19: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.20: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.21: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.22: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.23: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.24: `intel-ucode` — affected >=0 <20191113-r0
- Alpine:v3.10: `xen` — affected >=0 <4.12.1-r1
- Alpine:v3.11: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.12: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.13: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.14: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.15: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.16: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.17: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.18: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.13.0-r0

## Details
TSX Asynchronous Abort condition on some CPUs utilizing speculative execution may allow an authenticated user to potentially enable information disclosure via a side channel with local access.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11135
