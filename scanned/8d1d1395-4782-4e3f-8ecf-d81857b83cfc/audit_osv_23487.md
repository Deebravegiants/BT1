# [H] perf: Fix perf_pending_task() UaF

## Summary
Severity: High
Advisory: CVE-2022-48950
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48950
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.77 <5.15.84, >=6.0.7 <6.0.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf: Fix perf_pending_task() UaF

Per syzbot it is possible for perf_pending_task() to run after the
event is free()'d. There are two related but distinct cases:

 - the task_work was already queued before destroying the event;
 - destroying the event itself queues the task_work.

The first cannot be solved using task_work_cancel() since
perf_release() itself might be called from a task_work (____fput),
which means the current->task_works list is already empty and
task_work_cancel() won't be able to find the perf_pending_task()
entry.

The simplest alternative is extending the perf_event lifetime to cover
the task_work.

The second is just silly, queueing a task_work while you know the
event is going away makes no sense and is easily avoided by
re-arranging how the event is marked STATE_DEAD and ensuring it goes
through STATE_OFF on the way down.

## References
- https://git.kernel.org/stable/c/517e6a301f34613bff24a8e35b5455884f2d83d8
- https://git.kernel.org/stable/c/78e1317a174edbfd1182599bf76c092a2877672c
- https://git.kernel.org/stable/c/8bffa95ac19ff27c8261904f89d36c7fcf215d59
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48950.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48950
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
