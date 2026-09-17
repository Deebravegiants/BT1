# [H] mlxsw: spectrum_acl_tcam: Fix possible use-after-free during rehash

## Summary
Severity: High
Advisory: CVE-2024-35854
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35854
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.158, >=5.16.0 <6.1.90, >=6.2.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mlxsw: spectrum_acl_tcam: Fix possible use-after-free during rehash

The rehash delayed work migrates filters from one region to another
according to the number of available credits.

The migrated from region is destroyed at the end of the work if the
number of credits is non-negative as the assumption is that this is
indicative of migration being complete. This assumption is incorrect as
a non-negative number of credits can also be the result of a failed
migration.

The destruction of a region that still has filters referencing it can
result in a use-after-free [1].

Fix by not destroying the region if migration failed.

[1]
BUG: KASAN: slab-use-after-free in mlxsw_sp_acl_ctcam_region_entry_remove+0x21d/0x230
Read of size 8 at addr ffff8881735319e8 by task kworker/0:31/3858

CPU: 0 PID: 3858 Comm: kworker/0:31 Tainted: G        W          6.9.0-rc2-custom-00782-gf2275c2157d8 #5
Hardware name: Mellanox Technologies Ltd. MSN3700/VMOD0005, BIOS 5.11 01/06/2019
Workqueue: mlxsw_core mlxsw_sp_acl_tcam_vregion_rehash_work
Call Trace:
 <TASK>
 dump_stack_lvl+0xc6/0x120
 print_report+0xce/0x670
 kasan_report+0xd7/0x110
 mlxsw_sp_acl_ctcam_region_entry_remove+0x21d/0x230
 mlxsw_sp_acl_ctcam_entry_del+0x2e/0x70
 mlxsw_sp_acl_atcam_entry_del+0x81/0x210
 mlxsw_sp_acl_tcam_vchunk_migrate_all+0x3cd/0xb50
 mlxsw_sp_acl_tcam_vregion_rehash_work+0x157/0x1300
 process_one_work+0x8eb/0x19b0
 worker_thread+0x6c9/0xf70
 kthread+0x2c9/0x3b0
 ret_from_fork+0x4d/0x80
 ret_from_fork_asm+0x1a/0x30
 </TASK>

Allocated by task 174:
 kasan_save_stack+0x33/0x60
 kasan_save_track+0x14/0x30
 __kasan_kmalloc+0x8f/0xa0
 __kmalloc+0x19c/0x360
 mlxsw_sp_acl_tcam_region_create+0xdf/0x9c0
 mlxsw_sp_acl_tcam_vregion_rehash_work+0x954/0x1300
 process_one_work+0x8eb/0x19b0
 worker_thread+0x6c9/0xf70
 kthread+0x2c9/0x3b0
 ret_from_fork+0x4d/0x80
 ret_from_fork_asm+0x1a/0x30

Freed by task 7:
 kasan_save_stack+0x33/0x60
 kasan_save_track+0x14/0x30
 kasan_save_free_info+0x3b/0x60
 poison_slab_object+0x102/0x170
 __kasan_slab_free+0x14/0x30
 kfree+0xc1/0x290
 mlxsw_sp_acl_tcam_region_destroy+0x272/0x310
 mlxsw_sp_acl_tcam_vregion_rehash_work+0x731/0x1300
 process_one_work+0x8eb/0x19b0
 worker_thread+0x6c9/0xf70
 kthread+0x2c9/0x3b0
 ret_from_fork+0x4d/0x80
 ret_from_fork_asm+0x1a/0x30

## References
- https://git.kernel.org/stable/c/311eeaa7b9e26aba5b3d57b09859f07d8e9fc049
- https://git.kernel.org/stable/c/4c89642ca47fb620914780c7c51d8d1248201121
- https://git.kernel.org/stable/c/54225988889931467a9b55fdbef534079b665519
- https://git.kernel.org/stable/c/813e2ab753a8f8c243a39ede20c2e0adc15f3887
- https://git.kernel.org/stable/c/a02687044e124f8ccb427cd3632124a4e1a7d7c1
- https://git.kernel.org/stable/c/a429a912d6c779807f4d72a6cc0a1efaaa3613e1
- https://git.kernel.org/stable/c/e118e7ea24d1392878ef85926627c6bc640c4388
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35854.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35854
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
