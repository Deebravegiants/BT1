# [H] blk-iocost: do not WARN if iocg was already offlined

## Summary
Severity: High
Advisory: CVE-2024-36908
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36908
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-iocost: do not WARN if iocg was already offlined

In iocg_pay_debt(), warn is triggered if 'active_list' is empty, which
is intended to confirm iocg is active when it has debt. However, warn
can be triggered during a blkcg or disk removal, if iocg_waitq_timer_fn()
is run at that time:

  WARNING: CPU: 0 PID: 2344971 at block/blk-iocost.c:1402 iocg_pay_debt+0x14c/0x190
  Call trace:
  iocg_pay_debt+0x14c/0x190
  iocg_kick_waitq+0x438/0x4c0
  iocg_waitq_timer_fn+0xd8/0x130
  __run_hrtimer+0x144/0x45c
  __hrtimer_run_queues+0x16c/0x244
  hrtimer_interrupt+0x2cc/0x7b0

The warn in this situation is meaningless. Since this iocg is being
removed, the state of the 'active_list' is irrelevant, and 'waitq_timer'
is canceled after removing 'active_list' in ioc_pd_free(), which ensures
iocg is freed after iocg_waitq_timer_fn() returns.

Therefore, add the check if iocg was already offlined to avoid warn
when removing a blkcg or disk.

## References
- https://git.kernel.org/stable/c/01bc4fda9ea0a6b52f12326486f07a4910666cf6
- https://git.kernel.org/stable/c/14b3275f93d4a0d8ddc02195bc4e9869b7a3700e
- https://git.kernel.org/stable/c/1c172ac7afe4442964f4153b2c78fe4e005d9d67
- https://git.kernel.org/stable/c/56a9d07f427378eeb75b917bb49c6fbea8204126
- https://git.kernel.org/stable/c/7d215e013d097ed6fc4b0ad0272c9514214dc408
- https://git.kernel.org/stable/c/aed0aac18f039dd4af13c143063754efca358cb0
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36908.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36908
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
