# [H] ALPINE-CVE-2024-45817

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-45817
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-09-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-45817
Type: osv

## Affected
- Alpine:v3.17: `xen` — affected >=4.5.0 <4.16.6-r2
- Alpine:v3.18: `xen` — affected >=4.5.0 <4.17.5-r1
- Alpine:v3.19: `xen` — affected >=4.5.0 <4.18.3-r0
- Alpine:v3.20: `xen` — affected >=4.5.0 <4.18.3-r0
- Alpine:v3.21: `xen` — affected >=4.5.0 <4.19.0-r0
- Alpine:v3.22: `xen` — affected >=4.5.0 <4.19.0-r0
- Alpine:v3.23: `xen` — affected >=4.5.0 <4.19.0-r0
- Alpine:v3.24: `xen` — affected >=4.5.0 <4.19.0-r0

## Details
In x86's APIC (Advanced Programmable Interrupt Controller) architecture,
error conditions are reported in a status register.  Furthermore, the OS
can opt to receive an interrupt when a new error occurs.

It is possible to configure the error interrupt with an illegal vector,
which generates an error when an error interrupt is raised.

This case causes Xen to recurse through vlapic_error().  The recursion
itself is bounded; errors accumulate in the the status register and only
generate an interrupt when a new status bit becomes set.

However, the lock protecting this state in Xen will try to be taken
recursively, and deadlock.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-45817
