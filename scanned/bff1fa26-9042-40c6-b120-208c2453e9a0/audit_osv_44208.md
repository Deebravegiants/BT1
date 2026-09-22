# [C] block: stop the timeout timer when releasing a never added disk

## Summary
Severity: Critical
Advisory: CVE-2026-80589
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80589
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: stop the timeout timer when releasing a never added disk

disk_release() undoes blk_mq_init_allocated_queue() for a disk whose
probe failed before add_disk(), but it only calls blk_mq_exit_queue().
Nothing there stops q->timeout, and that timer rolls forward: it stays
pending until it next expires, not until the last request completes.
So if the driver issued any I/O before adding the disk, the
request_queue is freed while still linked into a timer wheel bucket.

Commit 6f8191fdf41d ("block: simplify disk shutdown") dropped the
blk_cleanup_queue() call that used to stop it.  __del_gendisk() and
blk_mq_destroy_queue() still do; only the probe failure path lost it.

nvme gets there because nvme_update_ns_info() submits Report Zones or
FDP io-mgmt-recv on ns->queue before the disk is added, so a later
failure - a concurrent reset setting NVME_CTRL_FROZEN, or
device_add_disk() failing - lands in put_disk() with the timer armed:

  BUG: KASAN: slab-use-after-free in detach_if_pending+0x30c/0x340
  Write of size 8 at addr ffff888004d71310 by task kworker/u8:2/37
   __timer_delete_sync+0x156/0x240 kernel/time/timer.c:1621
   blk_sync_queue+0x22/0x40 block/blk-core.c:222
   nvme_sync_queues+0x100/0x150 drivers/nvme/host/core.c:5362
   nvme_reset_work+0x138/0x930 drivers/nvme/host/pci.c:3264

  Allocated by task 34:
   __blk_mq_alloc_disk+0x33/0x100 block/blk-mq.c:4462
   nvme_alloc_ns+0x290/0x3870 drivers/nvme/host/core.c:4146

  Freed by task 0:
   blk_free_queue_rcu+0x3a/0x50 block/blk-core.c:254
   rcu_core+0xc10/0x1730 kernel/rcu/tree.c:2857

The queue being synced there is ctrl->admin_q, only a victim sharing a
timer wheel bucket with the freed queue's dangling entry; other runs
tripped in enqueue_timer(), __run_timers() or blk_mq_timeout_work().
Failing nvme_alloc_ns() with a debug patch makes it deterministic: one
leaked timer trips KASAN within seconds, while 1987 patched releases
produced no splat.

Stop the timer and the queue work items before blk_mq_exit_queue(), like
blk_mq_destroy_queue() does.

Found by FuzzNvme.

## References
- https://git.kernel.org/stable/c/1a0ae4d502062a2759f2a92d12bdeab3c64c7372
- https://git.kernel.org/stable/c/26cb8ebbfaf713c82e142d08828d4d765057633b
- https://git.kernel.org/stable/c/6ae7364f68e6c7af6b6df4bbb14040b89e5975d0
- https://git.kernel.org/stable/c/6f06dbe5012c160e0dba418a5a9cb16c456ad46a
- https://git.kernel.org/stable/c/93d620519d71dfc6ee64b5baea74f1d85d4439fb
- https://git.kernel.org/stable/c/bb03b56d1d754908a37a160603be21769da423cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80589.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80589
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
