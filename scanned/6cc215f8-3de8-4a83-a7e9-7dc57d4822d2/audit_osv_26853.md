# [H] f2fs: fix to check readonly condition correctly

## Summary
Severity: High
Advisory: CVE-2023-54182
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54182
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to check readonly condition correctly

With below case, it can mount multi-device image w/ rw option, however
one of secondary device is set as ro, later update will cause panic, so
let's introduce f2fs_dev_is_readonly(), and check multi-devices rw status
in f2fs_remount() w/ it in order to avoid such inconsistent mount status.

mkfs.f2fs -c /dev/zram1 /dev/zram0 -f
blockdev --setro /dev/zram1
mount -t f2fs dev/zram0 /mnt/f2fs
mount: /mnt/f2fs: WARNING: source write-protected, mounted read-only.
mount -t f2fs -o remount,rw mnt/f2fs
dd if=/dev/zero  of=/mnt/f2fs/file bs=1M count=8192

kernel BUG at fs/f2fs/inline.c:258!
RIP: 0010:f2fs_write_inline_data+0x23e/0x2d0 [f2fs]
Call Trace:
  f2fs_write_single_data_page+0x26b/0x9f0 [f2fs]
  f2fs_write_cache_pages+0x389/0xa60 [f2fs]
  __f2fs_write_data_pages+0x26b/0x2d0 [f2fs]
  f2fs_write_data_pages+0x2e/0x40 [f2fs]
  do_writepages+0xd3/0x1b0
  __writeback_single_inode+0x5b/0x420
  writeback_sb_inodes+0x236/0x5a0
  __writeback_inodes_wb+0x56/0xf0
  wb_writeback+0x2a3/0x490
  wb_do_writeback+0x2b2/0x330
  wb_workfn+0x6a/0x260
  process_one_work+0x270/0x5e0
  worker_thread+0x52/0x3e0
  kthread+0xf4/0x120
  ret_from_fork+0x29/0x50

## References
- https://git.kernel.org/stable/c/d78dfefcde9d311284434560d69c0478c55a657e
- https://git.kernel.org/stable/c/da8c535b28696017e5d1532d12ea78e836432d9e
- https://git.kernel.org/stable/c/e05d63f8b48aad4613bd582c945bee41e2dd7255
- https://git.kernel.org/stable/c/e2759a59a4cc96af712084e9db7065c858c4fe9f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54182.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54182
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
