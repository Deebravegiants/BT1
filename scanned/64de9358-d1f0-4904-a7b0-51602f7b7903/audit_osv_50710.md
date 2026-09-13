# [M] CVE-2020-29567

## Summary
Severity: Medium
Advisory: CVE-2020-29567
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-29567
Type: osv

## Details
An issue was discovered in Xen 4.14.x. When moving IRQs between CPUs to distribute the load of IRQ handling, IRQ vectors are dynamically allocated and de-allocated on the relevant CPUs. De-allocation has to happen when certain constraints are met. If these conditions are not met when first checked, the checking CPU may send an interrupt to itself, in the expectation that this IRQ will be delivered only after the condition preventing the cleanup has cleared. For two specific IRQ vectors, this expectation was violated, resulting in a continuous stream of self-interrupts, which renders the CPU effectively unusable. A domain with a passed through PCI device can cause lockup of a physical CPU, resulting in a Denial of Service (DoS) to the entire host. Only x86 systems are vulnerable. Arm systems are not vulnerable. Only guests with physical PCI devices passed through to them can exploit the vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OBLV6L6Q24PPQ2CRFXDX4Q76KU776GKI/
- https://security.gentoo.org/glsa/202107-30
- https://xenbits.xenproject.org/xsa/advisory-356.html
