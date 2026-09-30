# [M] CVE-2021-47569

## Summary
Severity: Medium
Advisory: CVE-2021-47569
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47569
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: fail cancellation for EXITING tasks

WARNING: CPU: 1 PID: 20 at fs/io_uring.c:6269 io_try_cancel_userdata+0x3c5/0x640 fs/io_uring.c:6269
CPU: 1 PID: 20 Comm: kworker/1:0 Not tainted 5.16.0-rc1-syzkaller #0
Workqueue: events io_fallback_req_func
RIP: 0010:io_try_cancel_userdata+0x3c5/0x640 fs/io_uring.c:6269
Call Trace:
 <TASK>
 io_req_task_link_timeout+0x6b/0x1e0 fs/io_uring.c:6886
 io_fallback_req_func+0xf9/0x1ae fs/io_uring.c:1334
 process_one_work+0x9b2/0x1690 kernel/workqueue.c:2298
 worker_thread+0x658/0x11f0 kernel/workqueue.c:2445
 kthread+0x405/0x4f0 kernel/kthread.c:327
 ret_from_fork+0x1f/0x30 arch/x86/entry/entry_64.S:295
 </TASK>

We need original task's context to do cancellations, so if it's dying
and the callback is executed in a fallback mode, fail the cancellation
attempt.

## References
- https://git.kernel.org/stable/c/3d2a1e68fd9904fdc1b02f2e7d40ca47df7ba39f
- https://git.kernel.org/stable/c/617a89484debcd4e7999796d693cf0b77d2519de
