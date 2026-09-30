# [C] netfs: Fix oops in write-retry from mis-resetting the subreq iterator

## Summary
Severity: Critical
Advisory: CVE-2025-38139
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38139
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.37, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix oops in write-retry from mis-resetting the subreq iterator

Fix the resetting of the subrequest iterator in netfs_retry_write_stream()
to use the iterator-reset function as the iterator may have been shortened
by a previous retry.  In such a case, the amount of data to be written by
the subrequest is not "subreq->len" but "subreq->len -
subreq->transferred".

Without this, KASAN may see an error in iov_iter_revert():

   BUG: KASAN: slab-out-of-bounds in iov_iter_revert lib/iov_iter.c:633 [inline]
   BUG: KASAN: slab-out-of-bounds in iov_iter_revert+0x443/0x5a0 lib/iov_iter.c:611
   Read of size 4 at addr ffff88802912a0b8 by task kworker/u32:7/1147

   CPU: 1 UID: 0 PID: 1147 Comm: kworker/u32:7 Not tainted 6.15.0-rc6-syzkaller-00052-g9f35e33144ae #0 PREEMPT(full)
   Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.3-debian-1.16.3-2~bpo12+1 04/01/2014
   Workqueue: events_unbound netfs_write_collection_worker
   Call Trace:
    <TASK>
    __dump_stack lib/dump_stack.c:94 [inline]
    dump_stack_lvl+0x116/0x1f0 lib/dump_stack.c:120
    print_address_description mm/kasan/report.c:408 [inline]
    print_report+0xc3/0x670 mm/kasan/report.c:521
    kasan_report+0xe0/0x110 mm/kasan/report.c:634
    iov_iter_revert lib/iov_iter.c:633 [inline]
    iov_iter_revert+0x443/0x5a0 lib/iov_iter.c:611
    netfs_retry_write_stream fs/netfs/write_retry.c:44 [inline]
    netfs_retry_writes+0x166d/0x1a50 fs/netfs/write_retry.c:231
    netfs_collect_write_results fs/netfs/write_collect.c:352 [inline]
    netfs_write_collection_worker+0x23fd/0x3830 fs/netfs/write_collect.c:374
    process_one_work+0x9cf/0x1b70 kernel/workqueue.c:3238
    process_scheduled_works kernel/workqueue.c:3319 [inline]
    worker_thread+0x6c8/0xf10 kernel/workqueue.c:3400
    kthread+0x3c2/0x780 kernel/kthread.c:464
    ret_from_fork+0x45/0x80 arch/x86/kernel/process.c:153
    ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:245
    </TASK>

## References
- https://git.kernel.org/stable/c/4481f7f2b3df123ec77e828c849138f75cff2bf2
- https://git.kernel.org/stable/c/bd0edaf99a920b1a9decd773179caacacb61d0fd
- https://git.kernel.org/stable/c/e0fefe9bc07e6101fdc57abda3644f296c114e31
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38139.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38139
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
