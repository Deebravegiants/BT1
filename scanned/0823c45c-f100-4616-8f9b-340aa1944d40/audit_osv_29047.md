# [H] net: wwan: t7xx: Fix FSM command timeout issue

## Summary
Severity: High
Advisory: CVE-2024-39282
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-39282
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.124, >=6.2.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: wwan: t7xx: Fix FSM command timeout issue

When driver processes the internal state change command, it use an
asynchronous thread to process the command operation. If the main
thread detects that the task has timed out, the asynchronous thread
will panic when executing the completion notification because the
main thread completion object has been released.

BUG: unable to handle page fault for address: fffffffffffffff8
PGD 1f283a067 P4D 1f283a067 PUD 1f283c067 PMD 0
Oops: 0000 [#1] PREEMPT SMP NOPTI
RIP: 0010:complete_all+0x3e/0xa0
[...]
Call Trace:
 <TASK>
 ? __die_body+0x68/0xb0
 ? page_fault_oops+0x379/0x3e0
 ? exc_page_fault+0x69/0xa0
 ? asm_exc_page_fault+0x22/0x30
 ? complete_all+0x3e/0xa0
 fsm_main_thread+0xa3/0x9c0 [mtk_t7xx (HASH:1400 5)]
 ? __pfx_autoremove_wake_function+0x10/0x10
 kthread+0xd8/0x110
 ? __pfx_fsm_main_thread+0x10/0x10 [mtk_t7xx (HASH:1400 5)]
 ? __pfx_kthread+0x10/0x10
 ret_from_fork+0x38/0x50
 ? __pfx_kthread+0x10/0x10
 ret_from_fork_asm+0x1b/0x30
 </TASK>
[...]
CR2: fffffffffffffff8
---[ end trace 0000000000000000 ]---

Use the reference counter to ensure safe release as Sergey suggests:
https://lore.kernel.org/all/da90f64c-260a-4329-87bf-1f9ff20a5951@gmail.com/

## References
- https://git.kernel.org/stable/c/0cd3bde081cd3452c875fa1e5c55834c670d6e05
- https://git.kernel.org/stable/c/4f619d518db9cd1a933c3a095a5f95d0c1584ae8
- https://git.kernel.org/stable/c/b8ab9bd0c8855cd5a6f4e0265083576257ff3fc5
- https://git.kernel.org/stable/c/e6e6882a1590cbdaca77a31a02f4954327237e14
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39282.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39282
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
