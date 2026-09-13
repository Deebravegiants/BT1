# [H] io_uring: lock overflowing for IOPOLL

## Summary
Severity: High
Advisory: CVE-2023-52903
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2023-52903
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.10.165, >=5.11.0 <5.15.89, >=5.16.0 <6.1.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: lock overflowing for IOPOLL

syzbot reports an issue with overflow filling for IOPOLL:

WARNING: CPU: 0 PID: 28 at io_uring/io_uring.c:734 io_cqring_event_overflow+0x1c0/0x230 io_uring/io_uring.c:734
CPU: 0 PID: 28 Comm: kworker/u4:1 Not tainted 6.2.0-rc3-syzkaller-16369-g358a161a6a9e #0
Workqueue: events_unbound io_ring_exit_work
Call trace:
 io_cqring_event_overflow+0x1c0/0x230 io_uring/io_uring.c:734
 io_req_cqe_overflow+0x5c/0x70 io_uring/io_uring.c:773
 io_fill_cqe_req io_uring/io_uring.h:168 [inline]
 io_do_iopoll+0x474/0x62c io_uring/rw.c:1065
 io_iopoll_try_reap_events+0x6c/0x108 io_uring/io_uring.c:1513
 io_uring_try_cancel_requests+0x13c/0x258 io_uring/io_uring.c:3056
 io_ring_exit_work+0xec/0x390 io_uring/io_uring.c:2869
 process_one_work+0x2d8/0x504 kernel/workqueue.c:2289
 worker_thread+0x340/0x610 kernel/workqueue.c:2436
 kthread+0x12c/0x158 kernel/kthread.c:376
 ret_from_fork+0x10/0x20 arch/arm64/kernel/entry.S:863

There is no real problem for normal IOPOLL as flush is also called with
uring_lock taken, but it's getting more complicated for IOPOLL|SQPOLL,
for which __io_cqring_overflow_flush() happens from the CQ waiting path.

## References
- https://git.kernel.org/stable/c/544d163d659d45a206d8929370d5a2984e546cb7
- https://git.kernel.org/stable/c/7fc3990dad04a677606337ebc61964094d6cb41b
- https://git.kernel.org/stable/c/de77faee280163ff03b7ab64af6c9d779a43d4c4
- https://git.kernel.org/stable/c/ed4629d1e968359fbb91d0a3780b1e86a2c08845
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52903.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52903
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
