# [H] bpf: Fix race in devmap on PREEMPT_RT

## Summary
Severity: High
Advisory: CVE-2026-23294
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23294
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix race in devmap on PREEMPT_RT

On PREEMPT_RT kernels, the per-CPU xdp_dev_bulk_queue (bq) can be
accessed concurrently by multiple preemptible tasks on the same CPU.

The original code assumes bq_enqueue() and __dev_flush() run atomically
with respect to each other on the same CPU, relying on
local_bh_disable() to prevent preemption. However, on PREEMPT_RT,
local_bh_disable() only calls migrate_disable() (when
PREEMPT_RT_NEEDS_BH_LOCK is not set) and does not disable
preemption, which allows CFS scheduling to preempt a task during
bq_xmit_all(), enabling another task on the same CPU to enter
bq_enqueue() and operate on the same per-CPU bq concurrently.

This leads to several races:

1. Double-free / use-after-free on bq->q[]: bq_xmit_all() snapshots
   cnt = bq->count, then iterates bq->q[0..cnt-1] to transmit frames.
   If preempted after the snapshot, a second task can call bq_enqueue()
   -> bq_xmit_all() on the same bq, transmitting (and freeing) the
   same frames. When the first task resumes, it operates on stale
   pointers in bq->q[], causing use-after-free.

2. bq->count and bq->q[] corruption: concurrent bq_enqueue() modifying
   bq->count and bq->q[] while bq_xmit_all() is reading them.

3. dev_rx/xdp_prog teardown race: __dev_flush() clears bq->dev_rx and
   bq->xdp_prog after bq_xmit_all(). If preempted between
   bq_xmit_all() return and bq->dev_rx = NULL, a preempting
   bq_enqueue() sees dev_rx still set (non-NULL), skips adding bq to
   the flush_list, and enqueues a frame. When __dev_flush() resumes,
   it clears dev_rx and removes bq from the flush_list, orphaning the
   newly enqueued frame.

4. __list_del_clearprev() on flush_node: similar to the cpumap race,
   both tasks can call __list_del_clearprev() on the same flush_node,
   the second dereferences the prev pointer already set to NULL.

The race between task A (__dev_flush -> bq_xmit_all) and task B
(bq_enqueue -> bq_xmit_all) on the same CPU:

  Task A (xdp_do_flush)          Task B (ndo_xdp_xmit redirect)
  ----------------------         --------------------------------
  __dev_flush(flush_list)
    bq_xmit_all(bq)
      cnt = bq->count  /* e.g. 16 */
      /* start iterating bq->q[] */
    <-- CFS preempts Task A -->
                                   bq_enqueue(dev, xdpf)
                                     bq->count == DEV_MAP_BULK_SIZE
                                     bq_xmit_all(bq, 0)
                                       cnt = bq->count  /* same 16! */
                                       ndo_xdp_xmit(bq->q[])
                                       /* frames freed by driver */
                                       bq->count = 0
    <-- Task A resumes -->
      ndo_xdp_xmit(bq->q[])
      /* use-after-free: frames already freed! */

Fix this by adding a local_lock_t to xdp_dev_bulk_queue and acquiring
it in bq_enqueue() and __dev_flush(). These paths already run under
local_bh_disable(), so use local_lock_nested_bh() which on non-RT is
a pure annotation with no overhead, and on PREEMPT_RT provides a
per-CPU sleeping lock that serializes access to the bq.

## References
- https://git.kernel.org/stable/c/1872e75375c40add4a35990de3be77b5741c252c
- https://git.kernel.org/stable/c/6c10b019785dc282c5f45d21e4a3f468b8fd6476
- https://git.kernel.org/stable/c/ab1a56c9d99189aa5c6e03940d06e40ba6a28240
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23294.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23294
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
