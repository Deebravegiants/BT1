# [M] CVE-2020-29571

## Summary
Severity: Medium
Advisory: CVE-2020-29571
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-29571
Type: osv

## Details
An issue was discovered in Xen through 4.14.x. A bounds check common to most operation time functions specific to FIFO event channels depends on the CPU observing consistent state. While the producer side uses appropriately ordered writes, the consumer side isn't protected against re-ordered reads, and may hence end up de-referencing a NULL pointer. Malicious or buggy guest kernels can mount a Denial of Service (DoS) attack affecting the entire system. Only Arm systems may be vulnerable. Whether a system is vulnerable depends on the specific CPU. x86 systems are not vulnerable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2C6M6S3CIMEBACH6O7V4H2VDANMO6TVA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OBLV6L6Q24PPQ2CRFXDX4Q76KU776GKI/
- https://security.gentoo.org/glsa/202107-30
- https://www.debian.org/security/2020/dsa-4812
- https://xenbits.xenproject.org/xsa/advisory-359.html
