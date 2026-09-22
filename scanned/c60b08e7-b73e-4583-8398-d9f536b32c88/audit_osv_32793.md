# [H] scsi: ufs: exynos: Disable iocc if dma-coherent property isn't set

## Summary
Severity: High
Advisory: CVE-2025-37977
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37977
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.12.26, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ufs: exynos: Disable iocc if dma-coherent property isn't set

If dma-coherent property isn't set then descriptors are non-cacheable
and the iocc shareability bits should be disabled. Without this UFS can
end up in an incompatible configuration and suffer from random cache
related stability issues.

## References
- https://git.kernel.org/stable/c/869749e48115ef944eeabec8e84138908471fa51
- https://git.kernel.org/stable/c/f0c6728a6f2e269ebb234a9b5bb6c2c24aafeb51
- https://git.kernel.org/stable/c/f92bb7436802f8eb7ee72dc911a33c8897fde366
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37977.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37977
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
