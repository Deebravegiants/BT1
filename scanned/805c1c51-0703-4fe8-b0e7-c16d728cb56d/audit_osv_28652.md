# [H] irqchip/gic-v3-its: Prevent double free on error

## Summary
Severity: High
Advisory: CVE-2024-35847
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35847
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <4.19.313, >=4.20.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.158, >=5.16.0 <6.1.90, >=6.2.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/gic-v3-its: Prevent double free on error

The error handling path in its_vpe_irq_domain_alloc() causes a double free
when its_vpe_init() fails after successfully allocating at least one
interrupt. This happens because its_vpe_irq_domain_free() frees the
interrupts along with the area bitmap and the vprop_page and
its_vpe_irq_domain_alloc() subsequently frees the area bitmap and the
vprop_page again.

Fix this by unconditionally invoking its_vpe_irq_domain_free() which
handles all cases correctly and by removing the bitmap/vprop_page freeing
from its_vpe_irq_domain_alloc().

[ tglx: Massaged change log ]

## References
- https://git.kernel.org/stable/c/03170e657f62c26834172742492a8cb8077ef792
- https://git.kernel.org/stable/c/5b012f77abde89bf0be8a0547636184fea618137
- https://git.kernel.org/stable/c/5dbdbe1133911ca7d8466bb86885adec32ad9438
- https://git.kernel.org/stable/c/aa44d21574751a7d6bca892eb8e0e9ac68372e52
- https://git.kernel.org/stable/c/b72d2b1448b682844f995e660b77f2a1fabc1662
- https://git.kernel.org/stable/c/c26591afd33adce296c022e3480dea4282b7ef91
- https://git.kernel.org/stable/c/dd681710ab77c8beafe2e263064cb1bd0e2d6ca9
- https://git.kernel.org/stable/c/f5417ff561b8ac9a7e53c747b8627a7ab58378ae
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35847.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35847
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
