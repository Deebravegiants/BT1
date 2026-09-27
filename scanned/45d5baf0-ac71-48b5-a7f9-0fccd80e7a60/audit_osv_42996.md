# [H] LoongArch: KVM: Validate irqchip index in irqfd routing

## Summary
Severity: High
Advisory: CVE-2026-72295
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72295
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: KVM: Validate irqchip index in irqfd routing

Sashiko reported that the irqchip index is not validated for LoongArch.
Add validation and reject out-of-range irqchip indexes to avoid indexing
past the routing table's chip array.

## References
- https://git.kernel.org/stable/c/199b570d7fca1aa70e596f10a6276997becffb6d
- https://git.kernel.org/stable/c/3474037904c20ff915e3ebab0ab5c1e41bbe549e
- https://git.kernel.org/stable/c/8b3e188d19e4ffe916780aeb7ddad9d6457b8bcc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72295.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72295
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
