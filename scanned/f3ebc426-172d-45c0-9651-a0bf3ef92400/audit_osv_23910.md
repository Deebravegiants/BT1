# [M] i2c: piix4: Fix a memory leak in the EFCH MMIO support

## Summary
Severity: Medium
Advisory: CVE-2022-49653
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49653
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.54, >=5.16.0 <5.18.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: piix4: Fix a memory leak in the EFCH MMIO support

The recently added support for EFCH MMIO regions introduced a memory
leak in that code path. The leak is caused by the fact that
release_resource() merely removes the resource from the tree but does
not free its memory. We need to call release_mem_region() instead,
which does free the memory. As a nice side effect, this brings back
some symmetry between the legacy and MMIO paths.

## References
- https://git.kernel.org/stable/c/8ad59b397f86a4d8014966fdc0552095a0c4fb2b
- https://git.kernel.org/stable/c/a3263e4cf8265f0c9eb0ed8a9b50f132c7a42e19
- https://git.kernel.org/stable/c/d2bf1a6480e8d44658a8ac3bdcec081238873212
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49653.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49653
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
