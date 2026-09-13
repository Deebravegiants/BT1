# [C] vdpa/octeon_ep: fix IRQ-to-ring mapping in interrupt handler

## Summary
Severity: Critical
Advisory: CVE-2026-74309
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74309
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

vdpa/octeon_ep: fix IRQ-to-ring mapping in interrupt handler

Look up the IRQ index in oct_hw->irqs instead of assuming
irq - irqs[0]. This supports non-contiguous IRQ numbers and
avoids incorrect ring indexing when irqs[0] is not the base.

## References
- https://git.kernel.org/stable/c/0d21a1d6375a05274291e32c1ab7cd57dbb69513
- https://git.kernel.org/stable/c/3ef0cfa77a3d526591be069850d186c255e3f0cc
- https://git.kernel.org/stable/c/c6c7eae5de798442987619434171ac886035d57c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74309.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74309
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
