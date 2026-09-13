# [H] drm/xe/guc_submit: fix race around suspend_pending

## Summary
Severity: High
Advisory: CVE-2024-56552
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56552
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/guc_submit: fix race around suspend_pending

Currently in some testcases we can trigger:

xe 0000:03:00.0: [drm] Assertion `exec_queue_destroyed(q)` failed!
....
WARNING: CPU: 18 PID: 2640 at drivers/gpu/drm/xe/xe_guc_submit.c:1826 xe_guc_sched_done_handler+0xa54/0xef0 [xe]
xe 0000:03:00.0: [drm] *ERROR* GT1: DEREGISTER_DONE: Unexpected engine state 0x00a1, guc_id=57

Looking at a snippet of corresponding ftrace for this GuC id we can see:

162.673311: xe_sched_msg_add:     dev=0000:03:00.0, gt=1 guc_id=57, opcode=3
162.673317: xe_sched_msg_recv:    dev=0000:03:00.0, gt=1 guc_id=57, opcode=3
162.673319: xe_exec_queue_scheduling_disable: dev=0000:03:00.0, 1:0x2, gt=1, width=1, guc_id=57, guc_state=0x29, flags=0x0
162.674089: xe_exec_queue_kill:   dev=0000:03:00.0, 1:0x2, gt=1, width=1, guc_id=57, guc_state=0x29, flags=0x0
162.674108: xe_exec_queue_close:  dev=0000:03:00.0, 1:0x2, gt=1, width=1, guc_id=57, guc_state=0xa9, flags=0x0
162.674488: xe_exec_queue_scheduling_done: dev=0000:03:00.0, 1:0x2, gt=1, width=1, guc_id=57, guc_state=0xa9, flags=0x0
162.678452: xe_exec_queue_deregister: dev=0000:03:00.0, 1:0x2, gt=1, width=1, guc_id=57, guc_state=0xa1, flags=0x0

It looks like we try to suspend the queue (opcode=3), setting
suspend_pending and triggering a disable_scheduling. The user then
closes the queue. However the close will also forcefully signal the
suspend fence after killing the queue, later when the G2H response for
disable_scheduling comes back we have now cleared suspend_pending when
signalling the suspend fence, so the disable_scheduling now incorrectly
tries to also deregister the queue. This leads to warnings since the queue
has yet to even be marked for destruction. We also seem to trigger
errors later with trying to double unregister the same queue.

To fix this tweak the ordering when handling the response to ensure we
don't race with a disable_scheduling that didn't actually intend to
perform an unregister.  The destruction path should now also correctly
wait for any pending_disable before marking as destroyed.

(cherry picked from commit f161809b362f027b6d72bd998e47f8f0bad60a2e)

## References
- https://git.kernel.org/stable/c/5ddcb50b700221fa7d7be2adcb3d7d7afe8633dd
- https://git.kernel.org/stable/c/87651f31ae4e6e6e7e6c7270b9b469405e747407
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56552.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56552
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
