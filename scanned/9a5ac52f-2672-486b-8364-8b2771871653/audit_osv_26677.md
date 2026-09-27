# [H] f2fs: fix to avoid use-after-free for cached IPU bio

## Summary
Severity: High
Advisory: CVE-2023-53537
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53537
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to avoid use-after-free for cached IPU bio

xfstest generic/019 reports a bug:

kernel BUG at mm/filemap.c:1619!
RIP: 0010:folio_end_writeback+0x8a/0x90
Call Trace:
 end_page_writeback+0x1c/0x60
 f2fs_write_end_io+0x199/0x420
 bio_endio+0x104/0x180
 submit_bio_noacct+0xa5/0x510
 submit_bio+0x48/0x80
 f2fs_submit_write_bio+0x35/0x300
 f2fs_submit_merged_ipu_write+0x2a0/0x2b0
 f2fs_write_single_data_page+0x838/0x8b0
 f2fs_write_cache_pages+0x379/0xa30
 f2fs_write_data_pages+0x30c/0x340
 do_writepages+0xd8/0x1b0
 __writeback_single_inode+0x44/0x370
 writeback_sb_inodes+0x233/0x4d0
 __writeback_inodes_wb+0x56/0xf0
 wb_writeback+0x1dd/0x2d0
 wb_workfn+0x367/0x4a0
 process_one_work+0x21d/0x430
 worker_thread+0x4e/0x3c0
 kthread+0x103/0x130
 ret_from_fork+0x2c/0x50

The root cause is: after cp_error is set, f2fs_submit_merged_ipu_write()
in f2fs_write_single_data_page() tries to flush IPU bio in cache, however
f2fs_submit_merged_ipu_write() missed to check validity of @bio parameter,
result in submitting random cached bio which belong to other IO context,
then it will cause use-after-free issue, fix it by adding additional
validity check.

## References
- https://git.kernel.org/stable/c/5cdb422c839134273866208dad5360835ddb9794
- https://git.kernel.org/stable/c/7d058f0ab161437369ad6e45a4b67c2886e71373
- https://git.kernel.org/stable/c/97ec6f1788cc6bee3f8c89cb908e1a2a1cd859bb
- https://git.kernel.org/stable/c/9a7f63283af6befc0f91d549f4f6917dff7479a9
- https://git.kernel.org/stable/c/af4ce124d7bd74cb839bbdaccffbb416771a56b5
- https://git.kernel.org/stable/c/b2f423fda64fb49213aa0ed5056079cf295a5df2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53537.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53537
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
