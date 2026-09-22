# [M] CVE-2021-47335

## Summary
Severity: Medium
Advisory: CVE-2021-47335
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47335
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to avoid racing on fsync_entry_slab by multi filesystem instances

As syzbot reported, there is an use-after-free issue during f2fs recovery:

Use-after-free write at 0xffff88823bc16040 (in kfence-#10):
 kmem_cache_destroy+0x1f/0x120 mm/slab_common.c:486
 f2fs_recover_fsync_data+0x75b0/0x8380 fs/f2fs/recovery.c:869
 f2fs_fill_super+0x9393/0xa420 fs/f2fs/super.c:3945
 mount_bdev+0x26c/0x3a0 fs/super.c:1367
 legacy_get_tree+0xea/0x180 fs/fs_context.c:592
 vfs_get_tree+0x86/0x270 fs/super.c:1497
 do_new_mount fs/namespace.c:2905 [inline]
 path_mount+0x196f/0x2be0 fs/namespace.c:3235
 do_mount fs/namespace.c:3248 [inline]
 __do_sys_mount fs/namespace.c:3456 [inline]
 __se_sys_mount+0x2f9/0x3b0 fs/namespace.c:3433
 do_syscall_64+0x3f/0xb0 arch/x86/entry/common.c:47
 entry_SYSCALL_64_after_hwframe+0x44/0xae

The root cause is multi f2fs filesystem instances can race on accessing
global fsync_entry_slab pointer, result in use-after-free issue of slab
cache, fixes to init/destroy this slab cache only once during module
init/destroy procedure to avoid this issue.

## References
- https://git.kernel.org/stable/c/79fa5d944c875711253a23b8155b36883c696409
- https://git.kernel.org/stable/c/86786603014e0a22d0d6af8e80ae4b8687927048
- https://git.kernel.org/stable/c/cad83c968c2ebe97905f900326988ed37146c347
- https://git.kernel.org/stable/c/e472b276a0d2180808009be38105e12754432e2a
