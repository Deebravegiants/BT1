# [M] ALPINE-CVE-2024-2193

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-2193
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-2193
Type: osv

## Affected
- Alpine:v3.16: `xen` — affected >=0 <4.16.5-r7
- Alpine:v3.17: `xen` — affected >=0 <4.16.5-r7
- Alpine:v3.18: `xen` — affected >=0 <4.17.3-r1
- Alpine:v3.19: `xen` — affected >=0 <4.18.0-r4
- Alpine:v3.20: `xen` — affected >=0 <4.18.0-r5
- Alpine:v3.21: `xen` — affected >=0 <4.18.0-r5
- Alpine:v3.22: `xen` — affected >=0 <4.18.0-r5
- Alpine:v3.23: `xen` — affected >=0 <4.18.0-r5
- Alpine:v3.24: `xen` — affected >=0 <4.18.0-r5

## Details
A Speculative Race Condition (SRC) vulnerability that impacts modern CPU architectures supporting speculative execution (related to Spectre V1) has been disclosed. An unauthenticated attacker can exploit this vulnerability to disclose arbitrary data from the CPU using race conditions to access the speculative executable code paths.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-2193
