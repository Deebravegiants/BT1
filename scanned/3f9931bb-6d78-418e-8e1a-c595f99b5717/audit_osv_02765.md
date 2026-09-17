# [M] ALPINE-CVE-2023-20569

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-20569
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-08-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-20569
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=0 <4.15.5-r0
- Alpine:v3.16: `xen` — affected >=0 <4.16.5-r0
- Alpine:v3.17: `xen` — affected >=0 <4.16.5-r0
- Alpine:v3.18: `xen` — affected >=0 <4.17.2-r0
- Alpine:v3.19: `xen` — affected >=0 <4.17.2-r0
- Alpine:v3.20: `xen` — affected >=0 <4.17.2-r0
- Alpine:v3.21: `xen` — affected >=0 <4.17.2-r0
- Alpine:v3.22: `xen` — affected >=0 <4.17.2-r0
- Alpine:v3.23: `xen` — affected >=0 <4.17.2-r0
- Alpine:v3.24: `xen` — affected >=0 <4.17.2-r0

## Details
A side channel vulnerability on some of the AMD CPUs may allow an attacker to influence the return address prediction. This may result in speculative execution at an attacker-controlled address, potentially leading to information disclosure.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-20569
