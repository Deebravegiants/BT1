# [H] mm/gup: fix gup_pud_range() for dax

## Summary
Severity: High
Advisory: CVE-2022-48986
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48986
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.227, >=5.5.0 <5.10.159, >=5.11.0 <5.15.83, >=5.16.0 <6.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/gup: fix gup_pud_range() for dax

For dax pud, pud_huge() returns true on x86. So the function works as long
as hugetlb is configured. However, dax doesn't depend on hugetlb.
Commit 414fd080d125 ("mm/gup: fix gup_pmd_range() for dax") fixed
devmap-backed huge PMDs, but missed devmap-backed huge PUDs. Fix this as
well.

This fixes the below kernel panic:

general protection fault, probably for non-canonical address 0x69e7c000cc478: 0000 [#1] SMP
	< snip >
Call Trace:
<TASK>
get_user_pages_fast+0x1f/0x40
iov_iter_get_pages+0xc6/0x3b0
? mempool_alloc+0x5d/0x170
bio_iov_iter_get_pages+0x82/0x4e0
? bvec_alloc+0x91/0xc0
? bio_alloc_bioset+0x19a/0x2a0
blkdev_direct_IO+0x282/0x480
? __io_complete_rw_common+0xc0/0xc0
? filemap_range_has_page+0x82/0xc0
generic_file_direct_write+0x9d/0x1a0
? inode_update_time+0x24/0x30
__generic_file_write_iter+0xbd/0x1e0
blkdev_write_iter+0xb4/0x150
? io_import_iovec+0x8d/0x340
io_write+0xf9/0x300
io_issue_sqe+0x3c3/0x1d30
? sysvec_reschedule_ipi+0x6c/0x80
__io_queue_sqe+0x33/0x240
? fget+0x76/0xa0
io_submit_sqes+0xe6a/0x18d0
? __fget_light+0xd1/0x100
__x64_sys_io_uring_enter+0x199/0x880
? __context_tracking_enter+0x1f/0x70
? irqentry_exit_to_user_mode+0x24/0x30
? irqentry_exit+0x1d/0x30
? __context_tracking_exit+0xe/0x70
do_syscall_64+0x3b/0x90
entry_SYSCALL_64_after_hwframe+0x61/0xcb
RIP: 0033:0x7fc97c11a7be
	< snip >
</TASK>
---[ end trace 48b2e0e67debcaeb ]---
RIP: 0010:internal_get_user_pages_fast+0x340/0x990
	< snip >
Kernel panic - not syncing: Fatal exception
Kernel Offset: disabled

## References
- https://git.kernel.org/stable/c/04edfa3dc06ecfc6133a33bc7271298782dee875
- https://git.kernel.org/stable/c/3ac29732a2ffa64c7de13a072b0f2848b9c11037
- https://git.kernel.org/stable/c/e06d13c36ded750c72521b600293befebb4e56c5
- https://git.kernel.org/stable/c/f1cf856123ceb766c49967ec79b841030fa1741f
- https://git.kernel.org/stable/c/fcd0ccd836ffad73d98a66f6fea7b16f735ea920
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48986.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48986
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
