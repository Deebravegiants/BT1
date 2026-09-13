# [H] ublk: wait on ublk_dev_ready() instead of ub->completion

## Summary
Severity: High
Advisory: CVE-2026-68173
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68173
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ublk: wait on ublk_dev_ready() instead of ub->completion

ub->completion is only re-armed by a successful START_USER_RECOVERY. If
the ublk server sends END_USER_RECOVERY without one - e.g. its START
failed with -EBUSY and the error was ignored - the wait is satisfied by
the stale completion of the previous recovery cycle, and the device is
marked LIVE and the requeue list kicked while the FETCH stream is still
running and ubq->canceling is still set. The kick redispatches a
previously requeued request, __ublk_queue_rq_common() sees ->canceling
and parks it again via __ublk_abort_rq(), and after the last FETCH
clears ->canceling nothing ever kicks the requeue list again: the
request is stranded there while holding its tag. If it is the flush
machinery's flush_rq, every subsequent fsync piles up in uninterruptible
sleep and teardown hangs on tag draining. This matches a report of a
lost PREFLUSH with ext4 on top of ublk after daemon crash recovery.

ub->completion is an edge-triggered latch used as a proxy for the level
condition "every queue has fetched all I/O commands", which can regress
(F_BATCH's UNPREP, daemon death) and whose re-arm can be skipped. Drop
it and wait on the real condition instead: the new helper
ublk_wait_dev_ready_and_lock() waits on ublk_dev_ready() via
wait_var_event_interruptible(), woken from ublk_mark_io_ready(), then
re-checks it under ub->mutex, waiting again on regression, and returns
with the mutex held and readiness guaranteed.

Readiness becomes true in the same ub->mutex critical section that
clears the last queue's ->canceling, so END_USER_RECOVERY marks the
device LIVE and kicks the requeue list strictly after ->canceling
clears. The wait stays interruptible, so a server whose daemon died can
still be signalled out. For ublk_ctrl_start_dev() this replaces the
fail-fast -EINVAL on an F_BATCH ready->UNPREP regression with waiting
until the device is ready again.

## References
- https://git.kernel.org/stable/c/432a9b2780c0a01caf547bd1fc2fcf28aeb8d173
- https://git.kernel.org/stable/c/7dd26adf7e7d482af524e3a0cca4a81ef7c159d0
- https://git.kernel.org/stable/c/8f188dd11a1c2ad94caeaee36ef68bb8221d4a12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68173.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68173
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
