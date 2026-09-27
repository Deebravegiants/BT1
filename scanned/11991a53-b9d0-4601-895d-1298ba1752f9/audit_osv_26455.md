# [M] erofs: Fix detection of atomic context

## Summary
Severity: Medium
Advisory: CVE-2023-53231
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53231
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: Fix detection of atomic context

Current check for atomic context is not sufficient as
z_erofs_decompressqueue_endio can be called under rcu lock
from blk_mq_flush_plug_list(). See the stacktrace [1]

In such case we should hand off the decompression work for async
processing rather than trying to do sync decompression in current
context. Patch fixes the detection by checking for
rcu_read_lock_any_held() and while at it use more appropriate
!in_task() check than in_atomic().

Background: Historically erofs would always schedule a kworker for
decompression which would incur the scheduling cost regardless of
the context. But z_erofs_decompressqueue_endio() may not always
be in atomic context and we could actually benefit from doing the
decompression in z_erofs_decompressqueue_endio() if we are in
thread context, for example when running with dm-verity.
This optimization was later added in patch [2] which has shown
improvement in performance benchmarks.

==============================================
[1] Problem stacktrace
[name:core&]BUG: sleeping function called from invalid context at kernel/locking/mutex.c:291
[name:core&]in_atomic(): 0, irqs_disabled(): 0, non_block: 0, pid: 1615, name: CpuMonitorServi
[name:core&]preempt_count: 0, expected: 0
[name:core&]RCU nest depth: 1, expected: 0
CPU: 7 PID: 1615 Comm: CpuMonitorServi Tainted: G S      W  OE      6.1.25-android14-5-maybe-dirty-mainline #1
Hardware name: MT6897 (DT)
Call trace:
 dump_backtrace+0x108/0x15c
 show_stack+0x20/0x30
 dump_stack_lvl+0x6c/0x8c
 dump_stack+0x20/0x48
 __might_resched+0x1fc/0x308
 __might_sleep+0x50/0x88
 mutex_lock+0x2c/0x110
 z_erofs_decompress_queue+0x11c/0xc10
 z_erofs_decompress_kickoff+0x110/0x1a4
 z_erofs_decompressqueue_endio+0x154/0x180
 bio_endio+0x1b0/0x1d8
 __dm_io_complete+0x22c/0x280
 clone_endio+0xe4/0x280
 bio_endio+0x1b0/0x1d8
 blk_update_request+0x138/0x3a4
 blk_mq_plug_issue_direct+0xd4/0x19c
 blk_mq_flush_plug_list+0x2b0/0x354
 __blk_flush_plug+0x110/0x160
 blk_finish_plug+0x30/0x4c
 read_pages+0x2fc/0x370
 page_cache_ra_unbounded+0xa4/0x23c
 page_cache_ra_order+0x290/0x320
 do_sync_mmap_readahead+0x108/0x2c0
 filemap_fault+0x19c/0x52c
 __do_fault+0xc4/0x114
 handle_mm_fault+0x5b4/0x1168
 do_page_fault+0x338/0x4b4
 do_translation_fault+0x40/0x60
 do_mem_abort+0x60/0xc8
 el0_da+0x4c/0xe0
 el0t_64_sync_handler+0xd4/0xfc
 el0t_64_sync+0x1a0/0x1a4

[2] Link: https://lore.kernel.org/all/20210317035448.13921-1-huangjianan@oppo.com/

## References
- https://git.kernel.org/stable/c/12d0a24afd9ea58e581ea64d64e066f2027b28d9
- https://git.kernel.org/stable/c/597fb60c75132719687e173b75cab8f6eb1ca657
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53231.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53231
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
