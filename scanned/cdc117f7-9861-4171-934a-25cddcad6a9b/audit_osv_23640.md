# [M] jffs2: fix memory leak in jffs2_scan_medium

## Summary
Severity: Medium
Advisory: CVE-2022-49276
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49276
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

jffs2: fix memory leak in jffs2_scan_medium

If an error is returned in jffs2_scan_eraseblock() and some memory
has been added to the jffs2_summary *s, we can observe the following
kmemleak report:

--------------------------------------------
unreferenced object 0xffff88812b889c40 (size 64):
  comm "mount", pid 692, jiffies 4294838325 (age 34.288s)
  hex dump (first 32 bytes):
    40 48 b5 14 81 88 ff ff 01 e0 31 00 00 00 50 00  @H........1...P.
    00 00 01 00 00 00 01 00 00 00 02 00 00 00 09 08  ................
  backtrace:
    [<ffffffffae93a3a3>] __kmalloc+0x613/0x910
    [<ffffffffaf423b9c>] jffs2_sum_add_dirent_mem+0x5c/0xa0
    [<ffffffffb0f3afa8>] jffs2_scan_medium.cold+0x36e5/0x4794
    [<ffffffffb0f3dbe1>] jffs2_do_mount_fs.cold+0xa7/0x2267
    [<ffffffffaf40acf3>] jffs2_do_fill_super+0x383/0xc30
    [<ffffffffaf40c00a>] jffs2_fill_super+0x2ea/0x4c0
    [<ffffffffb0315d64>] mtd_get_sb+0x254/0x400
    [<ffffffffb0315f5f>] mtd_get_sb_by_nr+0x4f/0xd0
    [<ffffffffb0316478>] get_tree_mtd+0x498/0x840
    [<ffffffffaf40bd15>] jffs2_get_tree+0x25/0x30
    [<ffffffffae9f358d>] vfs_get_tree+0x8d/0x2e0
    [<ffffffffaea7a98f>] path_mount+0x50f/0x1e50
    [<ffffffffaea7c3d7>] do_mount+0x107/0x130
    [<ffffffffaea7c5c5>] __se_sys_mount+0x1c5/0x2f0
    [<ffffffffaea7c917>] __x64_sys_mount+0xc7/0x160
    [<ffffffffb10142f5>] do_syscall_64+0x45/0x70
unreferenced object 0xffff888114b54840 (size 32):
  comm "mount", pid 692, jiffies 4294838325 (age 34.288s)
  hex dump (first 32 bytes):
    c0 75 b5 14 81 88 ff ff 02 e0 02 00 00 00 02 00  .u..............
    00 00 84 00 00 00 44 00 00 00 6b 6b 6b 6b 6b a5  ......D...kkkkk.
  backtrace:
    [<ffffffffae93be24>] kmem_cache_alloc_trace+0x584/0x880
    [<ffffffffaf423b04>] jffs2_sum_add_inode_mem+0x54/0x90
    [<ffffffffb0f3bd44>] jffs2_scan_medium.cold+0x4481/0x4794
    [...]
unreferenced object 0xffff888114b57280 (size 32):
  comm "mount", pid 692, jiffies 4294838393 (age 34.357s)
  hex dump (first 32 bytes):
    10 d5 6c 11 81 88 ff ff 08 e0 05 00 00 00 01 00  ..l.............
    00 00 38 02 00 00 28 00 00 00 6b 6b 6b 6b 6b a5  ..8...(...kkkkk.
  backtrace:
    [<ffffffffae93be24>] kmem_cache_alloc_trace+0x584/0x880
    [<ffffffffaf423c34>] jffs2_sum_add_xattr_mem+0x54/0x90
    [<ffffffffb0f3a24f>] jffs2_scan_medium.cold+0x298c/0x4794
    [...]
unreferenced object 0xffff8881116cd510 (size 16):
  comm "mount", pid 692, jiffies 4294838395 (age 34.355s)
  hex dump (first 16 bytes):
    00 00 00 00 00 00 00 00 09 e0 60 02 00 00 6b a5  ..........`...k.
  backtrace:
    [<ffffffffae93be24>] kmem_cache_alloc_trace+0x584/0x880
    [<ffffffffaf423cc4>] jffs2_sum_add_xref_mem+0x54/0x90
    [<ffffffffb0f3b2e3>] jffs2_scan_medium.cold+0x3a20/0x4794
    [...]
--------------------------------------------

Therefore, we should call jffs2_sum_reset_collected(s) on exit to
release the memory added in s. In addition, a new tag "out_buf" is
added to prevent the NULL pointer reference caused by s being NULL.
(thanks to Zhang Yi for this analysis)

## References
- https://git.kernel.org/stable/c/455f4a23490bfcbedc8e5c245c463a59b19e5ddd
- https://git.kernel.org/stable/c/51dbb5e36d59f62e34d462b801c1068248149cfe
- https://git.kernel.org/stable/c/52ba0ab4f0a606f02a6163493378989faa1ec10a
- https://git.kernel.org/stable/c/82462324bf35b6b553400af1c1aa265069cee28f
- https://git.kernel.org/stable/c/9b0c69182f09b70779817af4dcf89780955d5c4c
- https://git.kernel.org/stable/c/9cdd3128874f5fe759e2c4e1360ab7fb96a8d1df
- https://git.kernel.org/stable/c/b26bbc0c122cad038831f226a4cb4de702225e16
- https://git.kernel.org/stable/c/b36bccb04e14cc0c1e2d0e92d477fe220314fad6
- https://git.kernel.org/stable/c/e711913463af916d777a4873068f415f1fe2ad33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49276.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49276
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
