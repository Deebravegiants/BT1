# [H] net/mlx5: Bridge, fix the crash caused by LAG state check

## Summary
Severity: High
Advisory: CVE-2025-21970
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21970
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.84, >=6.7.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Bridge, fix the crash caused by LAG state check

When removing LAG device from bridge, NETDEV_CHANGEUPPER event is
triggered. Driver finds the lower devices (PFs) to flush all the
offloaded entries. And mlx5_lag_is_shared_fdb is checked, it returns
false if one of PF is unloaded. In such case,
mlx5_esw_bridge_lag_rep_get() and its caller return NULL, instead of
the alive PF, and the flush is skipped.

Besides, the bridge fdb entry's lastuse is updated in mlx5 bridge
event handler. But this SWITCHDEV_FDB_ADD_TO_BRIDGE event can be
ignored in this case because the upper interface for bond is deleted,
and the entry will never be aged because lastuse is never updated.

To make things worse, as the entry is alive, mlx5 bridge workqueue
keeps sending that event, which is then handled by kernel bridge
notifier. It causes the following crash when accessing the passed bond
netdev which is already destroyed.

To fix this issue, remove such checks. LAG state is already checked in
commit 15f8f168952f ("net/mlx5: Bridge, verify LAG state when adding
bond to bridge"), driver still need to skip offload if LAG becomes
invalid state after initialization.

 Oops: stack segment: 0000 [#1] SMP
 CPU: 3 UID: 0 PID: 23695 Comm: kworker/u40:3 Tainted: G           OE      6.11.0_mlnx #1
 Tainted: [O]=OOT_MODULE, [E]=UNSIGNED_MODULE
 Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS rel-1.13.0-0-gf21b5a4aeb02-prebuilt.qemu.org 04/01/2014
 Workqueue: mlx5_bridge_wq mlx5_esw_bridge_update_work [mlx5_core]
 RIP: 0010:br_switchdev_event+0x2c/0x110 [bridge]
 Code: 44 00 00 48 8b 02 48 f7 00 00 02 00 00 74 69 41 54 55 53 48 83 ec 08 48 8b a8 08 01 00 00 48 85 ed 74 4a 48 83 fe 02 48 89 d3 <4c> 8b 65 00 74 23 76 49 48 83 fe 05 74 7e 48 83 fe 06 75 2f 0f b7
 RSP: 0018:ffffc900092cfda0 EFLAGS: 00010297
 RAX: ffff888123bfe000 RBX: ffffc900092cfe08 RCX: 00000000ffffffff
 RDX: ffffc900092cfe08 RSI: 0000000000000001 RDI: ffffffffa0c585f0
 RBP: 6669746f6e690a30 R08: 0000000000000000 R09: ffff888123ae92c8
 R10: 0000000000000000 R11: fefefefefefefeff R12: ffff888123ae9c60
 R13: 0000000000000001 R14: ffffc900092cfe08 R15: 0000000000000000
 FS:  0000000000000000(0000) GS:ffff88852c980000(0000) knlGS:0000000000000000
 CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
 CR2: 00007f15914c8734 CR3: 0000000002830005 CR4: 0000000000770ef0
 DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
 DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
 PKRU: 55555554
 Call Trace:
  <TASK>
  ? __die_body+0x1a/0x60
  ? die+0x38/0x60
  ? do_trap+0x10b/0x120
  ? do_error_trap+0x64/0xa0
  ? exc_stack_segment+0x33/0x50
  ? asm_exc_stack_segment+0x22/0x30
  ? br_switchdev_event+0x2c/0x110 [bridge]
  ? sched_balance_newidle.isra.149+0x248/0x390
  notifier_call_chain+0x4b/0xa0
  atomic_notifier_call_chain+0x16/0x20
  mlx5_esw_bridge_update+0xec/0x170 [mlx5_core]
  mlx5_esw_bridge_update_work+0x19/0x40 [mlx5_core]
  process_scheduled_works+0x81/0x390
  worker_thread+0x106/0x250
  ? bh_worker+0x110/0x110
  kthread+0xb7/0xe0
  ? kthread_park+0x80/0x80
  ret_from_fork+0x2d/0x50
  ? kthread_park+0x80/0x80
  ret_from_fork_asm+0x11/0x20
  </TASK>

## References
- https://git.kernel.org/stable/c/4b8eeed4fb105770ce6dc84a2c6ef953c7b71cbb
- https://git.kernel.org/stable/c/5dd8bf6ab1d6db40f5d09603759fa88caec19e7f
- https://git.kernel.org/stable/c/86ff45f5f61ae1d0d17f0f6d8797b052eacfd8f1
- https://git.kernel.org/stable/c/bd7e3a42800743a7748c83243e4cafc1b995d4c4
- https://git.kernel.org/stable/c/f7bf259a04271165ae667ad21cfc60c6413f25ca
- https://git.kernel.org/stable/c/f90c4d6572488e2bad38cca00f1c59174a538a1a
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21970.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21970
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
