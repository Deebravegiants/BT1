# [H] f2fs: fix to avoid out-of-boundary access in dnode page

## Summary
Severity: High
Advisory: CVE-2025-38677
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-30
Source: https://osv.dev/vulnerability/CVE-2025-38677
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to avoid out-of-boundary access in dnode page

As Jiaming Zhang reported:

 <TASK>
 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0x1c1/0x2a0 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:378 [inline]
 print_report+0x17e/0x800 mm/kasan/report.c:480
 kasan_report+0x147/0x180 mm/kasan/report.c:593
 data_blkaddr fs/f2fs/f2fs.h:3053 [inline]
 f2fs_data_blkaddr fs/f2fs/f2fs.h:3058 [inline]
 f2fs_get_dnode_of_data+0x1a09/0x1c40 fs/f2fs/node.c:855
 f2fs_reserve_block+0x53/0x310 fs/f2fs/data.c:1195
 prepare_write_begin fs/f2fs/data.c:3395 [inline]
 f2fs_write_begin+0xf39/0x2190 fs/f2fs/data.c:3594
 generic_perform_write+0x2c7/0x910 mm/filemap.c:4112
 f2fs_buffered_write_iter fs/f2fs/file.c:4988 [inline]
 f2fs_file_write_iter+0x1ec8/0x2410 fs/f2fs/file.c:5216
 new_sync_write fs/read_write.c:593 [inline]
 vfs_write+0x546/0xa90 fs/read_write.c:686
 ksys_write+0x149/0x250 fs/read_write.c:738
 do_syscall_x64 arch/x86/entry/syscall_64.c:63 [inline]
 do_syscall_64+0xf3/0x3d0 arch/x86/entry/syscall_64.c:94
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

The root cause is in the corrupted image, there is a dnode has the same
node id w/ its inode, so during f2fs_get_dnode_of_data(), it tries to
access block address in dnode at offset 934, however it parses the dnode
as inode node, so that get_dnode_addr() returns 360, then it tries to
access page address from 360 + 934 * 4 = 4096 w/ 4 bytes.

To fix this issue, let's add sanity check for node id of all direct nodes
during f2fs_get_dnode_of_data().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/6b7784ea07e6aa044f74b39d6b5af5e28746fc81
- https://git.kernel.org/stable/c/77de19b6867f2740cdcb6c9c7e50d522b47847a4
- https://git.kernel.org/stable/c/888aa660144bcb6ec07839da756ee46bfcf7fc53
- https://git.kernel.org/stable/c/901f62efd6e855f93d8b1175540f29f4dc45ba55
- https://git.kernel.org/stable/c/92ef491b506a0f4dd971a3a76f86f2d8f5370180
- https://git.kernel.org/stable/c/a650654365c57407413e9b1f6ff4d539bf2e99ca
- https://git.kernel.org/stable/c/ee4d13f5407cbdf1216cc258f45492075713889a
- https://git.kernel.org/stable/c/f1d5093d9fe9f3c74c123741c88666cc853b79c5
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38677.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38677
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
