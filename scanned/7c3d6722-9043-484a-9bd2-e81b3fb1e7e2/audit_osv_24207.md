# [M] irqchip/wpcm450: Fix memory leak in wpcm450_aic_of_init()

## Summary
Severity: Medium
Advisory: CVE-2022-50416
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50416
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/wpcm450: Fix memory leak in wpcm450_aic_of_init()

If of_iomap() failed, 'aic' should be freed before return. Otherwise
there is a memory leak.

## References
- https://git.kernel.org/stable/c/4208d4faf36573a507b5e5de17abe342e9276759
- https://git.kernel.org/stable/c/740efb64ca5e8f2b30ac843bc4ab07950479fed4
- https://git.kernel.org/stable/c/773c9d7f127f7a599d42ceed831de69f5aa22f03
- https://git.kernel.org/stable/c/bcbcb396e1a8bd4dcaabfb0d5b98abae70880470
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50416.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50416
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
