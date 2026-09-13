# [H] drm/xe: Fix error cleanup in xe_exec_queue_create_ioctl()

## Summary
Severity: High
Advisory: CVE-2026-52976
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52976
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Fix error cleanup in xe_exec_queue_create_ioctl()

Two error handling issues exist in xe_exec_queue_create_ioctl():

1. When xe_hw_engine_group_add_exec_queue() fails, the error path jumps
   to put_exec_queue which skips xe_exec_queue_kill(). If the VM is in
   preempt fence mode, xe_vm_add_compute_exec_queue() has already added
   the queue to the VM's compute exec queue list. Skipping the kill
   leaves the queue on that list, leading to a dangling pointer after
   the queue is freed.

2. When xa_alloc() fails after xe_hw_engine_group_add_exec_queue() has
   succeeded, the error path does not call
   xe_hw_engine_group_del_exec_queue() to remove the queue from the hw
   engine group list. The queue is then freed while still linked into
   the hw engine group, causing a use-after-free.

Fix both by:
- Changing the xe_hw_engine_group_add_exec_queue() failure path to jump
  to kill_exec_queue so that xe_exec_queue_kill() properly removes the
  queue from the VM's compute list.
- Adding a del_hw_engine_group label before kill_exec_queue for the
  xa_alloc() failure path, which removes the queue from the hw engine
  group before proceeding with the rest of the cleanup.

(cherry picked from commit 37c831f401746a45d510b312b0ed7a77b1e06ec8)

## References
- https://git.kernel.org/stable/c/1be55646d8a2035343b012dcb12210db7bb8b056
- https://git.kernel.org/stable/c/753b149d5a433eb19e0c1b0eb4526a6e26120d1f
- https://git.kernel.org/stable/c/f3cc22d4df3ed58439ea7e21daa54c3608e03b78
- https://git.kernel.org/stable/c/f93b00161213a0fe9f7ff1d8498ee5ca9e0a5c43
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52976.json
- https://access.redhat.com/errata/RHSA-2026:42919
- https://access.redhat.com/errata/RHSA-2026:45192
- https://access.redhat.com/errata/RHSA-2026:52667
- https://access.redhat.com/errata/RHSA-2026:52764
- https://access.redhat.com/security/cve/CVE-2026-52976
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52976.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52976
- https://bugzilla.redhat.com/show_bug.cgi?id=2492284
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
