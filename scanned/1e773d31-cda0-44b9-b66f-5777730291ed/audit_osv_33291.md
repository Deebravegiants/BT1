# [H] f2fs: fix to do sanity check on node footer for non inode dnode

## Summary
Severity: High
Advisory: CVE-2025-40025
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40025
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <6.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to do sanity check on node footer for non inode dnode

As syzbot reported below:

------------[ cut here ]------------
kernel BUG at fs/f2fs/file.c:1243!
Oops: invalid opcode: 0000 [#1] SMP KASAN NOPTI
CPU: 0 UID: 0 PID: 5354 Comm: syz.0.0 Not tainted 6.17.0-rc1-syzkaller-00211-g90d970cade8e #0 PREEMPT(full)
RIP: 0010:f2fs_truncate_hole+0x69e/0x6c0 fs/f2fs/file.c:1243
Call Trace:
 <TASK>
 f2fs_punch_hole+0x2db/0x330 fs/f2fs/file.c:1306
 f2fs_fallocate+0x546/0x990 fs/f2fs/file.c:2018
 vfs_fallocate+0x666/0x7e0 fs/open.c:342
 ksys_fallocate fs/open.c:366 [inline]
 __do_sys_fallocate fs/open.c:371 [inline]
 __se_sys_fallocate fs/open.c:369 [inline]
 __x64_sys_fallocate+0xc0/0x110 fs/open.c:369
 do_syscall_x64 arch/x86/entry/syscall_64.c:63 [inline]
 do_syscall_64+0xfa/0x3b0 arch/x86/entry/syscall_64.c:94
 entry_SYSCALL_64_after_hwframe+0x77/0x7f
RIP: 0033:0x7f1e65f8ebe9

w/ a fuzzed image, f2fs may encounter panic due to it detects inconsistent
truncation range in direct node in f2fs_truncate_hole().

The root cause is: a non-inode dnode may has the same footer.ino and
footer.nid, so the dnode will be parsed as an inode, then ADDRS_PER_PAGE()
may return wrong blkaddr count which may be 923 typically, by chance,
dn.ofs_in_node is equal to 923, then count can be calculated to 0 in below
statement, later it will trigger panic w/ f2fs_bug_on(, count == 0 || ...).

	count = min(end_offset - dn.ofs_in_node, pg_end - pg_start);

This patch introduces a new node_type NODE_TYPE_NON_INODE, then allowing
passing the new_type to sanity_check_node_footer in f2fs_get_node_folio()
to detect corruption that a non-inode dnode has the same footer.ino and
footer.nid.

Scripts to reproduce:
mkfs.f2fs -f /dev/vdb
mount /dev/vdb /mnt/f2fs
touch /mnt/f2fs/foo
touch /mnt/f2fs/bar
dd if=/dev/zero of=/mnt/f2fs/foo bs=1M count=8
umount /mnt/f2fs
inject.f2fs --node --mb i_nid --nid 4 --idx 0 --val 5 /dev/vdb
mount /dev/vdb /mnt/f2fs
xfs_io /mnt/f2fs/foo -c "fpunch 6984k 4k"

## References
- https://git.kernel.org/stable/c/186098f34b8a5d65eb828f952c8cc56272c60ea0
- https://git.kernel.org/stable/c/c18ecd99e0c707ef8f83cace861cbc3162f4fdf1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40025.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40025
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
