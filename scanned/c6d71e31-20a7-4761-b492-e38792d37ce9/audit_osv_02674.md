# [M] ALPINE-CVE-2022-42321

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-42321
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42321
Type: osv

## Affected
- Alpine:v3.14: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.15: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.16: `xen` — affected >=0 <4.16.3-r0
- Alpine:v3.17: `xen` — affected >=0 <4.16.3-r0
- Alpine:v3.18: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.17.0-r0

## Details
Xenstore: Guests can crash xenstored via exhausting the stack Xenstored is using recursion for some Xenstore operations (e.g. for deleting a sub-tree of Xenstore nodes). With sufficiently deep nesting levels this can result in stack exhaustion on xenstored, leading to a crash of xenstored.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42321
