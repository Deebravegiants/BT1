# [H] CVE-2021-47483

## Summary
Severity: High
Advisory: CVE-2021-47483
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47483
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

regmap: Fix possible double-free in regcache_rbtree_exit()

In regcache_rbtree_insert_to_block(), when 'present' realloc failed,
the 'blk' which is supposed to assign to 'rbnode->block' will be freed,
so 'rbnode->block' points a freed memory, in the error handling path of
regcache_rbtree_init(), 'rbnode->block' will be freed again in
regcache_rbtree_exit(), KASAN will report double-free as follows:

BUG: KASAN: double-free or invalid-free in kfree+0xce/0x390
Call Trace:
 slab_free_freelist_hook+0x10d/0x240
 kfree+0xce/0x390
 regcache_rbtree_exit+0x15d/0x1a0
 regcache_rbtree_init+0x224/0x2c0
 regcache_init+0x88d/0x1310
 __regmap_init+0x3151/0x4a80
 __devm_regmap_init+0x7d/0x100
 madera_spi_probe+0x10f/0x333 [madera_spi]
 spi_probe+0x183/0x210
 really_probe+0x285/0xc30

To fix this, moving up the assignment of rbnode->block to immediately after
the reallocation has succeeded so that the data structure stays valid even
if the second reallocation fails.

## References
- https://git.kernel.org/stable/c/50cc1462a668dc62949a1127388bc3af785ce047
- https://git.kernel.org/stable/c/55e6d8037805b3400096d621091dfbf713f97e83
- https://git.kernel.org/stable/c/758ced2c3878ff789801e6fee808e185c5cf08d6
- https://git.kernel.org/stable/c/e72dce9afbdbfa70d9b44f5908a50ff6c4858999
- https://git.kernel.org/stable/c/fc081477b47dfc3a6cb50a96087fc29674013fc2
- https://git.kernel.org/stable/c/1cead23c1c0bc766dacb900a3b0269f651ad596f
- https://git.kernel.org/stable/c/36e911a16b377bde0ad91a8c679069d0d310b1a6
- https://git.kernel.org/stable/c/3dae1a4eced3ee733d7222e69b8a55caf2d61091
