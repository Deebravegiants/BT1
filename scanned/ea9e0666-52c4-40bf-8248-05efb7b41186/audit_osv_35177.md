# [H] mlxsw: spectrum_mr: Fix use-after-free when updating multicast route stats

## Summary
Severity: High
Advisory: CVE-2025-68800
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68800
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mlxsw: spectrum_mr: Fix use-after-free when updating multicast route stats

Cited commit added a dedicated mutex (instead of RTNL) to protect the
multicast route list, so that it will not change while the driver
periodically traverses it in order to update the kernel about multicast
route stats that were queried from the device.

One instance of list entry deletion (during route replace) was missed
and it can result in a use-after-free [1].

Fix by acquiring the mutex before deleting the entry from the list and
releasing it afterwards.

[1]
BUG: KASAN: slab-use-after-free in mlxsw_sp_mr_stats_update+0x4a5/0x540 drivers/net/ethernet/mellanox/mlxsw/spectrum_mr.c:1006 [mlxsw_spectrum]
Read of size 8 at addr ffff8881523c2fa8 by task kworker/2:5/22043

CPU: 2 UID: 0 PID: 22043 Comm: kworker/2:5 Not tainted 6.18.0-rc1-custom-g1a3d6d7cd014 #1 PREEMPT(full)
Hardware name: Mellanox Technologies Ltd. MSN2010/SA002610, BIOS 5.6.5 08/24/2017
Workqueue: mlxsw_core mlxsw_sp_mr_stats_update [mlxsw_spectrum]
Call Trace:
 <TASK>
 dump_stack_lvl+0xba/0x110
 print_report+0x174/0x4f5
 kasan_report+0xdf/0x110
 mlxsw_sp_mr_stats_update+0x4a5/0x540 drivers/net/ethernet/mellanox/mlxsw/spectrum_mr.c:1006 [mlxsw_spectrum]
 process_one_work+0x9cc/0x18e0
 worker_thread+0x5df/0xe40
 kthread+0x3b8/0x730
 ret_from_fork+0x3e9/0x560
 ret_from_fork_asm+0x1a/0x30
 </TASK>

Allocated by task 29933:
 kasan_save_stack+0x30/0x50
 kasan_save_track+0x14/0x30
 __kasan_kmalloc+0x8f/0xa0
 mlxsw_sp_mr_route_add+0xd8/0x4770 [mlxsw_spectrum]
 mlxsw_sp_router_fibmr_event_work+0x371/0xad0 drivers/net/ethernet/mellanox/mlxsw/spectrum_router.c:7965 [mlxsw_spectrum]
 process_one_work+0x9cc/0x18e0
 worker_thread+0x5df/0xe40
 kthread+0x3b8/0x730
 ret_from_fork+0x3e9/0x560
 ret_from_fork_asm+0x1a/0x30

Freed by task 29933:
 kasan_save_stack+0x30/0x50
 kasan_save_track+0x14/0x30
 __kasan_save_free_info+0x3b/0x70
 __kasan_slab_free+0x43/0x70
 kfree+0x14e/0x700
 mlxsw_sp_mr_route_add+0x2dea/0x4770 drivers/net/ethernet/mellanox/mlxsw/spectrum_mr.c:444 [mlxsw_spectrum]
 mlxsw_sp_router_fibmr_event_work+0x371/0xad0 drivers/net/ethernet/mellanox/mlxsw/spectrum_router.c:7965 [mlxsw_spectrum]
 process_one_work+0x9cc/0x18e0
 worker_thread+0x5df/0xe40
 kthread+0x3b8/0x730
 ret_from_fork+0x3e9/0x560
 ret_from_fork_asm+0x1a/0x30

## References
- https://git.kernel.org/stable/c/216afc198484fde110ebeafc017992266f4596ce
- https://git.kernel.org/stable/c/37ca08b35a27ce8fd8e74dd3fd2ae21c23b63b73
- https://git.kernel.org/stable/c/4049a6ace209f4ed150429f86ae796d7d6a4c22b
- https://git.kernel.org/stable/c/5f2831fc593c2b2efbff7dd0dd7441cec76adcd5
- https://git.kernel.org/stable/c/6e367c361a523a4b54fe618215c64a0ee189caf0
- https://git.kernel.org/stable/c/8ac1dacec458f55f871f7153242ed6ab60373b90
- https://git.kernel.org/stable/c/b957366f5611bbaba03dd10ef861283347ddcc88
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68800.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68800
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
