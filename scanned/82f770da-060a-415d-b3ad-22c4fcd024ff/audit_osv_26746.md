# [H] regmap-irq: Fix out-of-bounds access when allocating config buffers

## Summary
Severity: High
Advisory: CVE-2023-53768
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2023-53768
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

regmap-irq: Fix out-of-bounds access when allocating config buffers

When allocating the 2D array for handling IRQ type registers in
regmap_add_irq_chip_fwnode(), the intent is to allocate a matrix
with num_config_bases rows and num_config_regs columns.

This is currently handled by allocating a buffer to hold a pointer for
each row (i.e. num_config_bases). After that, the logic attempts to
allocate the memory required to hold the register configuration for
each row. However, instead of doing this allocation for each row
(i.e. num_config_bases allocations), the logic erroneously does this
allocation num_config_regs number of times.

This scenario can lead to out-of-bounds accesses when num_config_regs
is greater than num_config_bases. Fix this by updating the terminating
condition of the loop that allocates the memory for holding the register
configuration to allocate memory only for each row in the matrix.

Amit Pundir reported a crash that was occurring on his db845c device
due to memory corruption (see "Closes" tag for Amit's report). The KASAN
report below helped narrow it down to this issue:

[   14.033877][    T1] ==================================================================
[   14.042507][    T1] BUG: KASAN: invalid-access in regmap_add_irq_chip_fwnode+0x594/0x1364
[   14.050796][    T1] Write of size 8 at addr 06ffff8081021850 by task init/1

[   14.242004][    T1] The buggy address belongs to the object at ffffff8081021850
[   14.242004][    T1]  which belongs to the cache kmalloc-8 of size 8
[   14.255669][    T1] The buggy address is located 0 bytes inside of
[   14.255669][    T1]  8-byte region [ffffff8081021850, ffffff8081021858)

## References
- https://git.kernel.org/stable/c/6e7b2337ecd028bd888a1a0be4115b8a88faf838
- https://git.kernel.org/stable/c/963b54df82b6d6206d7def273390bf3f7af558e1
- https://git.kernel.org/stable/c/b1a726ad33e585e3d9fa70712df31ae105e4532c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53768.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53768
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
