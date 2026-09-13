# [C] ksmbd: fix use-after-free in durable v2 replay of active file handles

## Summary
Severity: Critical
Advisory: CVE-2026-23427
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23427
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.130, >=6.7.0 <6.12.78, >=6.9.0 <6.18.20, >=6.13.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in durable v2 replay of active file handles

parse_durable_handle_context() unconditionally assigns dh_info->fp->conn
to the current connection when handling a DURABLE_REQ_V2 context with
SMB2_FLAGS_REPLAY_OPERATION. ksmbd_lookup_fd_cguid() does not filter by
fp->conn, so it returns file handles that are already actively connected.
The unconditional overwrite replaces fp->conn, and when the overwriting
connection is subsequently freed, __ksmbd_close_fd() dereferences the
stale fp->conn via spin_lock(&fp->conn->llist_lock), causing a
use-after-free.

KASAN report:

[    7.349357] ==================================================================
[    7.349607] BUG: KASAN: slab-use-after-free in _raw_spin_lock+0x75/0xe0
[    7.349811] Write of size 4 at addr ffff8881056ac18c by task kworker/1:2/108
[    7.350010]
[    7.350064] CPU: 1 UID: 0 PID: 108 Comm: kworker/1:2 Not tainted 7.0.0-rc3+ #58 PREEMPTLAZY
[    7.350068] Hardware name: QEMU Ubuntu 24.04 PC v2 (i440FX + PIIX, arch_caps fix, 1996), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
[    7.350070] Workqueue: ksmbd-io handle_ksmbd_work
[    7.350083] Call Trace:
[    7.350087]  <TASK>
[    7.350087]  dump_stack_lvl+0x64/0x80
[    7.350094]  print_report+0xce/0x660
[    7.350100]  ? __pfx__raw_spin_lock_irqsave+0x10/0x10
[    7.350101]  ? __pfx___mod_timer+0x10/0x10
[    7.350106]  ? _raw_spin_lock+0x75/0xe0
[    7.350108]  kasan_report+0xce/0x100
[    7.350109]  ? _raw_spin_lock+0x75/0xe0
[    7.350114]  kasan_check_range+0x105/0x1b0
[    7.350116]  _raw_spin_lock+0x75/0xe0
[    7.350118]  ? __pfx__raw_spin_lock+0x10/0x10
[    7.350119]  ? __call_rcu_common.constprop.0+0x25e/0x780
[    7.350125]  ? close_id_del_oplock+0x2cc/0x4e0
[    7.350128]  __ksmbd_close_fd+0x27f/0xaf0
[    7.350131]  ksmbd_close_fd+0x135/0x1b0
[    7.350133]  smb2_close+0xb19/0x15b0
[    7.350142]  ? __pfx_smb2_close+0x10/0x10
[    7.350143]  ? xas_load+0x18/0x270
[    7.350146]  ? _raw_spin_lock+0x84/0xe0
[    7.350148]  ? __pfx__raw_spin_lock+0x10/0x10
[    7.350150]  ? _raw_spin_unlock+0xe/0x30
[    7.350151]  ? ksmbd_smb2_check_message+0xeb2/0x24c0
[    7.350153]  ? ksmbd_tree_conn_lookup+0xcd/0xf0
[    7.350154]  handle_ksmbd_work+0x40f/0x1080
[    7.350156]  process_one_work+0x5fa/0xef0
[    7.350162]  ? assign_work+0x122/0x3e0
[    7.350163]  worker_thread+0x54b/0xf70
[    7.350165]  ? __pfx_worker_thread+0x10/0x10
[    7.350166]  kthread+0x346/0x470
[    7.350170]  ? recalc_sigpending+0x19b/0x230
[    7.350176]  ? __pfx_kthread+0x10/0x10
[    7.350178]  ret_from_fork+0x4fb/0x6c0
[    7.350183]  ? __pfx_ret_from_fork+0x10/0x10
[    7.350185]  ? __switch_to+0x36c/0xbe0
[    7.350188]  ? __pfx_kthread+0x10/0x10
[    7.350190]  ret_from_fork_asm+0x1a/0x30
[    7.350197]  </TASK>
[    7.350197]
[    7.355160] Allocated by task 123:
[    7.355261]  kasan_save_stack+0x33/0x60
[    7.355373]  kasan_save_track+0x14/0x30
[    7.355484]  __kasan_kmalloc+0x8f/0xa0
[    7.355593]  ksmbd_conn_alloc+0x44/0x6d0
[    7.355711]  ksmbd_kthread_fn+0x243/0xd70
[    7.355839]  kthread+0x346/0x470
[    7.355942]  ret_from_fork+0x4fb/0x6c0
[    7.356051]  ret_from_fork_asm+0x1a/0x30
[    7.356164]
[    7.356214] Freed by task 134:
[    7.356305]  kasan_save_stack+0x33/0x60
[    7.356416]  kasan_save_track+0x14/0x30
[    7.356527]  kasan_save_free_info+0x3b/0x60
[    7.356646]  __kasan_slab_free+0x43/0x70
[    7.356761]  kfree+0x1ca/0x430
[    7.356862]  ksmbd_tcp_disconnect+0x59/0xe0
[    7.356993]  ksmbd_conn_handler_loop+0x77e/0xd40
[    7.357138]  kthread+0x346/0x470
[    7.357240]  ret_from_fork+0x4fb/0x6c0
[    7.357350]  ret_from_fork_asm+0x1a/0x30
[    7.357463]
[    7.357513] The buggy address belongs to the object at ffff8881056ac000
[    7.357513]  which belongs to the cache kmalloc-1k of size 1024
[    7.357857] The buggy address is located 396 bytes inside of
[    7.357857]  freed 1024-byte region 
---truncated---

## References
- https://git.kernel.org/stable/c/568a25fd7bcdfb2790f7d42aa2a440dca4435c96
- https://git.kernel.org/stable/c/9b0792c3eacf01e67f356d6ef9707b0ae5022419
- https://git.kernel.org/stable/c/a5828c14a9e3d5eeed0bcc0a58f0f3fbca0cdcb2
- https://git.kernel.org/stable/c/b0158d9d6f4ec5941e49a0b812735db2844f9975
- https://git.kernel.org/stable/c/b425e4d0eb321a1116ddbf39636333181675d8f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23427.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23427
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
