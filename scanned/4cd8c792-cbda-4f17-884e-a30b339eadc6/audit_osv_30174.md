# [M] net/mlx5: Fix command bitmask initialization

## Summary
Severity: Medium
Advisory: CVE-2024-50147
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50147
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Fix command bitmask initialization

Command bitmask have a dedicated bit for MANAGE_PAGES command, this bit
isn't Initialize during command bitmask Initialization, only during
MANAGE_PAGES.

In addition, mlx5_cmd_trigger_completions() is trying to trigger
completion for MANAGE_PAGES command as well.

Hence, in case health error occurred before any MANAGE_PAGES command
have been invoke (for example, during mlx5_enable_hca()),
mlx5_cmd_trigger_completions() will try to trigger completion for
MANAGE_PAGES command, which will result in null-ptr-deref error.[1]

Fix it by Initialize command bitmask correctly.

While at it, re-write the code for better understanding.

[1]
BUG: KASAN: null-ptr-deref in mlx5_cmd_trigger_completions+0x1db/0x600 [mlx5_core]
Write of size 4 at addr 0000000000000214 by task kworker/u96:2/12078
CPU: 10 PID: 12078 Comm: kworker/u96:2 Not tainted 6.9.0-rc2_for_upstream_debug_2024_04_07_19_01 #1
Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS rel-1.13.0-0-gf21b5a4aeb02-prebuilt.qemu.org 04/01/2014
Workqueue: mlx5_health0000:08:00.0 mlx5_fw_fatal_reporter_err_work [mlx5_core]
Call Trace:
 <TASK>
 dump_stack_lvl+0x7e/0xc0
 kasan_report+0xb9/0xf0
 kasan_check_range+0xec/0x190
 mlx5_cmd_trigger_completions+0x1db/0x600 [mlx5_core]
 mlx5_cmd_flush+0x94/0x240 [mlx5_core]
 enter_error_state+0x6c/0xd0 [mlx5_core]
 mlx5_fw_fatal_reporter_err_work+0xf3/0x480 [mlx5_core]
 process_one_work+0x787/0x1490
 ? lockdep_hardirqs_on_prepare+0x400/0x400
 ? pwq_dec_nr_in_flight+0xda0/0xda0
 ? assign_work+0x168/0x240
 worker_thread+0x586/0xd30
 ? rescuer_thread+0xae0/0xae0
 kthread+0x2df/0x3b0
 ? kthread_complete_and_exit+0x20/0x20
 ret_from_fork+0x2d/0x70
 ? kthread_complete_and_exit+0x20/0x20
 ret_from_fork_asm+0x11/0x20
 </TASK>

## References
- https://git.kernel.org/stable/c/2feac1e562be0efc621a6722644a90f355d53473
- https://git.kernel.org/stable/c/d1606090bb294cecb7de3c4ed177f5aa0abd4c4e
- https://git.kernel.org/stable/c/d62b14045c6511a7b2d4948d1a83a4e592deeb05
- https://git.kernel.org/stable/c/d88564c79d1cedaf2655f12261eca0d2796bde4e
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50147.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50147
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
