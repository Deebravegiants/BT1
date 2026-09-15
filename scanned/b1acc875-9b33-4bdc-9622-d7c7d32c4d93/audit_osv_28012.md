# [M] pci_iounmap(): Fix MMIO mapping leak

## Summary
Severity: Medium
Advisory: CVE-2024-26977
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26977
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

pci_iounmap(): Fix MMIO mapping leak

The #ifdef ARCH_HAS_GENERIC_IOPORT_MAP accidentally also guards iounmap(),
which means MMIO mappings are leaked.

Move the guard so we call iounmap() for MMIO mappings.

## References
- https://git.kernel.org/stable/c/5e4b23e7a7b33a1e56bfa3e5598138a2234d55b6
- https://git.kernel.org/stable/c/6d21d0356aa44157a62e39c0d1a13d4c69a8d0c8
- https://git.kernel.org/stable/c/7626913652cc786c238e2dd7d8740b17d41b2637
- https://git.kernel.org/stable/c/af280e137e273935f2e09f4d73169998298792ed
- https://git.kernel.org/stable/c/b5d40f02e7222da032c2042aebcf2a07de9b342f
- https://git.kernel.org/stable/c/f3749345a9b7295dd071d0ed589634cb46364f77
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26977.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26977
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
