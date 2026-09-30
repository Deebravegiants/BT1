# [H] Input: alps - fix use-after-free bugs caused by dev3_register_work

## Summary
Severity: High
Advisory: CVE-2025-68822
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68822
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: alps - fix use-after-free bugs caused by dev3_register_work

The dev3_register_work delayed work item is initialized within
alps_reconnect() and scheduled upon receipt of the first bare
PS/2 packet from an external PS/2 device connected to the ALPS
touchpad. During device detachment, the original implementation
calls flush_workqueue() in psmouse_disconnect() to ensure
completion of dev3_register_work. However, the flush_workqueue()
in psmouse_disconnect() only blocks and waits for work items that
were already queued to the workqueue prior to its invocation. Any
work items submitted after flush_workqueue() is called are not
included in the set of tasks that the flush operation awaits.
This means that after flush_workqueue() has finished executing,
the dev3_register_work could still be scheduled. Although the
psmouse state is set to PSMOUSE_CMD_MODE in psmouse_disconnect(),
the scheduling of dev3_register_work remains unaffected.

The race condition can occur as follows:

CPU 0 (cleanup path)     | CPU 1 (delayed work)
psmouse_disconnect()     |
  psmouse_set_state()    |
  flush_workqueue()      | alps_report_bare_ps2_packet()
  alps_disconnect()      |   psmouse_queue_work()
    kfree(priv); // FREE | alps_register_bare_ps2_mouse()
                         |   priv = container_of(work...); // USE
                         |   priv->dev3 // USE

Add disable_delayed_work_sync() in alps_disconnect() to ensure
that dev3_register_work is properly canceled and prevented from
executing after the alps_data structure has been deallocated.

This bug is identified by static analysis.

## References
- https://git.kernel.org/stable/c/a9c115e017b2c633d25bdfe6709dda6fc36f08c2
- https://git.kernel.org/stable/c/bf40644ef8c8a288742fa45580897ed0e0289474
- https://git.kernel.org/stable/c/ed8c61b89be0c45f029228b2913d5cf7b5cda1a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68822.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68822
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
