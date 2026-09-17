# [H] landlock: Fix LANDLOCK_SCOPE_SIGNAL bypass on the SIGIO path

## Summary
Severity: High
Advisory: CVE-2026-72183
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72183
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.101, >=6.13.0 <6.18.40, >=6.15.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

landlock: Fix LANDLOCK_SCOPE_SIGNAL bypass on the SIGIO path

LANDLOCK_SCOPE_SIGNAL must prevent a sandboxed process from signaling
processes outside its Landlock domain.  It can be bypassed through the
asynchronous SIGIO delivery path.

A sandboxed process that owns any file or socket can arm it with
fcntl(fd, F_SETOWN, -pgid), fcntl(fd, F_SETSIG, SIGKILL) and O_ASYNC, so
that an I/O event makes the kernel deliver the chosen signal to the
whole process group.  As the head of its process group's task list (the
default position right after fork()) that group can also hold the
non-sandboxed process that launched it, e.g. a supervisor or a security
monitor.  The sandbox can thus kill or signal the processes
LANDLOCK_SCOPE_SIGNAL is meant to protect from it.

The scope is enforced in hook_file_send_sigiotask() against the Landlock
domain recorded at F_SETOWN time, not the live domain of the sender.
control_current_fowner() decides whether to record that domain and skips
recording it when the fowner target is in the caller's thread group,
which is safe only for a single-task target (PIDTYPE_PID, PIDTYPE_TGID).
For a process group (PIDTYPE_PGID) pid_task() returns only one member;
recording is skipped whenever that member shares the caller's thread
group, and hook_file_send_sigiotask() then lets the signal fan out to
the whole group unchecked.

Record the domain for every non single-process target so the scope is
enforced against each group member at delivery time.

That recording is necessary but not sufficient on its own: the kernel
signals a process group through its members' thread-group leaders, and
the leader of the registrant's own process can carry a different
Landlock domain than the sibling thread that armed the owner.
domain_is_scoped() would then deny that leader, even though commit
18eb75f3af40 ("landlock: Always allow signals between threads of the
same process") requires same-process delivery to be allowed.
hook_task_kill() avoids this by evaluating same_thread_group() live, per
recipient; the SIGIO path instead delegates the whole decision to a
single registration-time check, which a process-group fan-out cannot
honor.

So also record the registrant's thread group next to its domain and
exempt it at delivery: hook_file_send_sigiotask() allows the signal
whenever the recipient belongs to the registrant's own process,
restoring the same-process guarantee while keeping out-of-domain group
members blocked.  The direct kill() path (hook_task_kill) already
evaluates the live domain and is unaffected.

[mic: Check pid_type earlier and improve comment, fix commit message,
fix comment formatting]

## References
- https://git.kernel.org/stable/c/04916f7dc6d37cd478b06c86398c34a6963ac8c9
- https://git.kernel.org/stable/c/1f18aac2637220b5847d073447498e81ddca10b2
- https://git.kernel.org/stable/c/4b80320ca7ed03d6e683f95b6066565dc97b9f92
- https://git.kernel.org/stable/c/7a92e9fd1d496a610b40e0c4253fd54e7496f5ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72183.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72183
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
