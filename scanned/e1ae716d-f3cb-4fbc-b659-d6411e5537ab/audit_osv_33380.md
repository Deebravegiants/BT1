# [H] nios2: ensure that memblock.current_limit is set when setting pfn limits

## Summary
Severity: High
Advisory: CVE-2025-40245
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40245
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.196, >=5.16.0 <6.1.158, >=6.2.0 <6.6.115, >=6.7.0 <6.12.56, >=6.13.0 <6.17.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nios2: ensure that memblock.current_limit is set when setting pfn limits

On nios2, with CONFIG_FLATMEM set, the kernel relies on
memblock_get_current_limit() to determine the limits of mem_map, in
particular for max_low_pfn.
Unfortunately, memblock.current_limit is only default initialized to
MEMBLOCK_ALLOC_ANYWHERE at this point of the bootup, potentially leading
to situations where max_low_pfn can erroneously exceed the value of
max_pfn and, thus, the valid range of available DRAM.

This can in turn cause kernel-level paging failures, e.g.:

[   76.900000] Unable to handle kernel paging request at virtual address 20303000
[   76.900000] ea = c0080890, ra = c000462c, cause = 14
[   76.900000] Kernel panic - not syncing: Oops
[   76.900000] ---[ end Kernel panic - not syncing: Oops ]---

This patch fixes this by pre-calculating memblock.current_limit
based on the upper limits of the available memory ranges via
adjust_lowmem_bounds, a simplified version of the equivalent
implementation within the arm architecture.

## References
- https://git.kernel.org/stable/c/25f09699edd360b534ccae16bc276c3b52c471f3
- https://git.kernel.org/stable/c/5c3e38a367822f036227dd52bac82dc4a05157e2
- https://git.kernel.org/stable/c/8912814f14e298b83df072fecc1f7ed1b63b1b2c
- https://git.kernel.org/stable/c/90f5f715550e07cd6a51f80fc3f062d832c8c997
- https://git.kernel.org/stable/c/a20b83cf45be2057f3d073506779e52c7fa17f94
- https://git.kernel.org/stable/c/b1ec9faef7e36269ca3ec890972a78effbaeb975
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40245.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40245
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
