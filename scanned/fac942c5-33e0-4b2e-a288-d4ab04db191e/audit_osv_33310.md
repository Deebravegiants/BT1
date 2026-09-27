# [H] RDMA/rxe: Fix race in do_task() when draining

## Summary
Severity: High
Advisory: CVE-2025-40061
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40061
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix race in do_task() when draining

When do_task() exhausts its iteration budget (!ret), it sets the state
to TASK_STATE_IDLE to reschedule, without a secondary check on the
current task->state. This can overwrite the TASK_STATE_DRAINING state
set by a concurrent call to rxe_cleanup_task() or rxe_disable_task().

While state changes are protected by a spinlock, both rxe_cleanup_task()
and rxe_disable_task() release the lock while waiting for the task to
finish draining in the while(!is_done(task)) loop. The race occurs if
do_task() hits its iteration limit and acquires the lock in this window.
The cleanup logic may then proceed while the task incorrectly
reschedules itself, leading to a potential use-after-free.

This bug was introduced during the migration from tasklets to workqueues,
where the special handling for the draining case was lost.

Fix this by restoring the original pre-migration behavior. If the state is
TASK_STATE_DRAINING when iterations are exhausted, set cont to 1 to
force a new loop iteration. This allows the task to finish its work, so
that a subsequent iteration can reach the switch statement and correctly
transition the state to TASK_STATE_DRAINED, stopping the task as intended.

## References
- https://git.kernel.org/stable/c/52edccfb555142678c836c285bf5b4ec760bd043
- https://git.kernel.org/stable/c/660b6959c4170637f5db2279d1f71af33a49e49b
- https://git.kernel.org/stable/c/85288bcf7ffe11e7b036edf91937bc62fd384076
- https://git.kernel.org/stable/c/8ca7eada62fcfabf6ec1dc7468941e791c1d8729
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40061.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40061
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
