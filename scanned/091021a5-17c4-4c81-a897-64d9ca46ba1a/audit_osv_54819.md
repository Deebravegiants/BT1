# [H] CVE-2024-45817

## Summary
Severity: High
Advisory: CVE-2024-45817
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-09-25
Source: https://osv.dev/vulnerability/CVE-2024-45817
Type: osv

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
- http://www.openwall.com/lists/oss-security/2024/09/24/1
- https://xenbits.xenproject.org/xsa/advisory-462.html
- http://xenbits.xen.org/xsa/advisory-462.html
