# [H] net/mlx5: Fix a race on command flush flow

## Summary
Severity: High
Advisory: CVE-2022-48858
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48858
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.185, >=5.5.0 <5.10.106, >=5.9.0 <5.15.29, >=5.11.0 <5.16.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Fix a race on command flush flow

Fix a refcount use after free warning due to a race on command entry.
Such race occurs when one of the commands releases its last refcount and
frees its index and entry while another process running command flush
flow takes refcount to this command entry. The process which handles
commands flush may see this command as needed to be flushed if the other
process released its refcount but didn't release the index yet. Fix it
by adding the needed spin lock.

It fixes the following warning trace:

refcount_t: addition on 0; use-after-free.
WARNING: CPU: 11 PID: 540311 at lib/refcount.c:25 refcount_warn_saturate+0x80/0xe0
...
RIP: 0010:refcount_warn_saturate+0x80/0xe0
...
Call Trace:
 <TASK>
 mlx5_cmd_trigger_completions+0x293/0x340 [mlx5_core]
 mlx5_cmd_flush+0x3a/0xf0 [mlx5_core]
 enter_error_state+0x44/0x80 [mlx5_core]
 mlx5_fw_fatal_reporter_err_work+0x37/0xe0 [mlx5_core]
 process_one_work+0x1be/0x390
 worker_thread+0x4d/0x3d0
 ? rescuer_thread+0x350/0x350
 kthread+0x141/0x160
 ? set_kthread_struct+0x40/0x40
 ret_from_fork+0x1f/0x30
 </TASK>

## References
- https://git.kernel.org/stable/c/0401bfb27a91d7bdd74b1635c1aae57cbb128da6
- https://git.kernel.org/stable/c/063bd355595428750803d8736a9bb7c8db67d42d
- https://git.kernel.org/stable/c/1a4017926eeea56c7540cc41b42106746ee8a0ee
- https://git.kernel.org/stable/c/7c519f769f555ff7d9d4ccba3497bbb589df360a
- https://git.kernel.org/stable/c/f3331bc17449f15832c31823f27573f4c0e13e5f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48858.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48858
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
