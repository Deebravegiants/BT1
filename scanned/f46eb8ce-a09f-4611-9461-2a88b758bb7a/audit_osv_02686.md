# [H] ALPINE-CVE-2022-42335

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-42335
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42335
Type: osv

## Affected
- Alpine:v3.18: `xen` — affected >=0 <4.17.0-r5
- Alpine:v3.19: `xen` — affected >=0 <4.17.0-r5
- Alpine:v3.20: `xen` — affected >=0 <4.17.0-r5
- Alpine:v3.21: `xen` — affected >=0 <4.17.0-r5
- Alpine:v3.22: `xen` — affected >=0 <4.17.0-r5
- Alpine:v3.23: `xen` — affected >=0 <4.17.0-r5
- Alpine:v3.24: `xen` — affected >=0 <4.17.0-r5

## Details
x86 shadow paging arbitrary pointer dereference In environments where host assisted address translation is necessary but Hardware Assisted Paging (HAP) is unavailable, Xen will run guests in so called shadow mode. Due to too lax a check in one of the hypervisor routines used for shadow page handling it is possible for a guest with a PCI device passed through to cause the hypervisor to access an arbitrary pointer partially under guest control.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42335
