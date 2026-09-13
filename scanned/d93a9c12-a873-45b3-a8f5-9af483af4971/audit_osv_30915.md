# [M] mfd: intel_soc_pmic_bxtwc: Use IRQ domain for PMIC devices

## Summary
Severity: Medium
Advisory: CVE-2024-56723
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56723
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mfd: intel_soc_pmic_bxtwc: Use IRQ domain for PMIC devices

While design wise the idea of converting the driver to use
the hierarchy of the IRQ chips is correct, the implementation
has (inherited) flaws. This was unveiled when platform_get_irq()
had started WARN() on IRQ 0 that is supposed to be a Linux
IRQ number (also known as vIRQ).

Rework the driver to respect IRQ domain when creating each MFD
device separately, as the domain is not the same for all of them.

## References
- https://git.kernel.org/stable/c/0350d783ab888cb1cb48ced36cc28b372723f1a4
- https://git.kernel.org/stable/c/61d590d7076b50b6ebdea1f3b83bb041c01fc482
- https://git.kernel.org/stable/c/6ea17c03edc7ed0aabb1431eb26e2f94849af68a
- https://git.kernel.org/stable/c/7ba45b8bc62e64da524d45532107ae93eb33c93c
- https://git.kernel.org/stable/c/897713c9d24f6ec394585abfcf259a6e5cad22c8
- https://git.kernel.org/stable/c/b3d45c19bcffb9a9a821df759f60be39d88c19f4
- https://git.kernel.org/stable/c/bb6642d4b3136359b5b620049f76515876e6127e
- https://git.kernel.org/stable/c/d4cc78bd6a25accb7ae2ac9fc445d1e1deda4a62
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56723.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56723
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
