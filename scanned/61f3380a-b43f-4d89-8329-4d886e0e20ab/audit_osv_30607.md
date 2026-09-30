# [H] f2fs: fix to account dirty data in __get_secs_required()

## Summary
Severity: High
Advisory: CVE-2024-53220
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53220
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to account dirty data in __get_secs_required()

It will trigger system panic w/ testcase in [1]:

------------[ cut here ]------------
kernel BUG at fs/f2fs/segment.c:2752!
RIP: 0010:new_curseg+0xc81/0x2110
Call Trace:
 f2fs_allocate_data_block+0x1c91/0x4540
 do_write_page+0x163/0xdf0
 f2fs_outplace_write_data+0x1aa/0x340
 f2fs_do_write_data_page+0x797/0x2280
 f2fs_write_single_data_page+0x16cd/0x2190
 f2fs_write_cache_pages+0x994/0x1c80
 f2fs_write_data_pages+0x9cc/0xea0
 do_writepages+0x194/0x7a0
 filemap_fdatawrite_wbc+0x12b/0x1a0
 __filemap_fdatawrite_range+0xbb/0xf0
 file_write_and_wait_range+0xa1/0x110
 f2fs_do_sync_file+0x26f/0x1c50
 f2fs_sync_file+0x12b/0x1d0
 vfs_fsync_range+0xfa/0x230
 do_fsync+0x3d/0x80
 __x64_sys_fsync+0x37/0x50
 x64_sys_call+0x1e88/0x20d0
 do_syscall_64+0x4b/0x110
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

The root cause is if checkpoint_disabling and lfs_mode are both on,
it will trigger OPU for all overwritten data, it may cost more free
segment than expected, so f2fs must account those data correctly to
calculate cosumed free segments later, and return ENOSPC earlier to
avoid run out of free segment during block allocation.

[1] https://lore.kernel.org/fstests/20241015025106.3203676-1-chao@kernel.org/

## References
- https://git.kernel.org/stable/c/1acd73edbbfef2c3c5b43cba4006a7797eca7050
- https://git.kernel.org/stable/c/6e58b2987960efcd917bc42da781cee256213618
- https://git.kernel.org/stable/c/9313b85ddc120e2d2f0efaf86d0204d4c98d60b1
- https://git.kernel.org/stable/c/e812871c068cc0f91ff9f5cee87d00df1c44aae4
- https://git.kernel.org/stable/c/f1b8bfe8d2f2fdf905d37c174d5bc1cd2b6910c5
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53220.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53220
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
