# [M] CVE-2023-46836

## Summary
Severity: Medium
Advisory: CVE-2023-46836
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/CVE-2023-46836
Type: osv

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
- https://xenbits.xenproject.org/xsa/advisory-446.html
- https://xenbits.xenproject.org/xsa/advisory-446.html
