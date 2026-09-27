# [M] ALPINE-CVE-2023-46836

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-46836
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46836
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=0 <4.15.5-r3
- Alpine:v3.16: `xen` — affected >=0 <4.16.5-r4
- Alpine:v3.17: `xen` — affected >=0 <4.16.5-r4
- Alpine:v3.18: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.19: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.20: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.21: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.22: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.23: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.24: `xen` — affected >=0 <4.17.2-r4

## Details
The fixes for XSA-422 (Branch Type Confusion) and XSA-434 (Speculative
Return Stack Overflow) are not IRQ-safe.  It was believed that the
mitigations always operated in contexts with IRQs disabled.

However, the original XSA-254 fix for Meltdown (XPTI) deliberately left
interrupts enabled on two entry paths; one unconditionally, and one
conditionally on whether XPTI was active.

As BTC/SRSO and Meltdown affect different CPU vendors, the mitigations
are not active together by default.  Therefore, there is a race
condition whereby a malicious PV guest can bypass BTC/SRSO protections
and launch a BTC/SRSO attack against Xen.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46836
