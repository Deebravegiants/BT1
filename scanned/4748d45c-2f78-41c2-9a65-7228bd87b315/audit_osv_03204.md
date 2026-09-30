# [H] ALPINE-CVE-2025-1713

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-1713
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-1713
Type: osv

## Affected
- Alpine:v3.18: `xen` — affected >=4.0.0 <4.17.5-r3
- Alpine:v3.19: `xen` — affected >=4.0.0 <4.18.4-r1
- Alpine:v3.20: `xen` — affected >=4.0.0 <4.18.4-r1
- Alpine:v3.21: `xen` — affected >=4.0.0 <4.19.2-r0
- Alpine:v3.22: `xen` — affected >=4.0.0 <4.19.1-r1
- Alpine:v3.23: `xen` — affected >=4.0.0 <4.19.1-r1
- Alpine:v3.24: `xen` — affected >=4.0.0 <4.19.1-r1

## Details
When setting up interrupt remapping for legacy PCI(-X) devices,
including PCI(-X) bridges, a lookup of the upstream bridge is required.
This lookup, itself involving acquiring of a lock, is done in a context
where acquiring that lock is unsafe.  This can lead to a deadlock.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-1713
