# [H] f2fs: fix return value of f2fs_convert_inline_inode()

## Summary
Severity: High
Advisory: CVE-2024-42296
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42296
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix return value of f2fs_convert_inline_inode()

If device is readonly, make f2fs_convert_inline_inode()
return EROFS instead of zero, otherwise it may trigger
panic during writeback of inline inode's dirty page as
below:

 f2fs_write_single_data_page+0xbb6/0x1e90 fs/f2fs/data.c:2888
 f2fs_write_cache_pages fs/f2fs/data.c:3187 [inline]
 __f2fs_write_data_pages fs/f2fs/data.c:3342 [inline]
 f2fs_write_data_pages+0x1efe/0x3a90 fs/f2fs/data.c:3369
 do_writepages+0x359/0x870 mm/page-writeback.c:2634
 filemap_fdatawrite_wbc+0x125/0x180 mm/filemap.c:397
 __filemap_fdatawrite_range mm/filemap.c:430 [inline]
 file_write_and_wait_range+0x1aa/0x290 mm/filemap.c:788
 f2fs_do_sync_file+0x68a/0x1ae0 fs/f2fs/file.c:276
 generic_write_sync include/linux/fs.h:2806 [inline]
 f2fs_file_write_iter+0x7bd/0x24e0 fs/f2fs/file.c:4977
 call_write_iter include/linux/fs.h:2114 [inline]
 new_sync_write fs/read_write.c:497 [inline]
 vfs_write+0xa72/0xc90 fs/read_write.c:590
 ksys_write+0x1a0/0x2c0 fs/read_write.c:643
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xf5/0x240 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

## References
- https://git.kernel.org/stable/c/077f0e24b27c4b44841593c7edbd1993be9eecb5
- https://git.kernel.org/stable/c/1e7725814361c8c008d131db195cef8274ff26b8
- https://git.kernel.org/stable/c/47a8ddcdcaccd9b891db4574795e46a33a121ac2
- https://git.kernel.org/stable/c/70f5ef5f33c333cfb286116fa3af74ac9bc84f1b
- https://git.kernel.org/stable/c/a8eb3de28e7a365690c61161e7a07a4fc7c60bbf
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42296.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42296
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
