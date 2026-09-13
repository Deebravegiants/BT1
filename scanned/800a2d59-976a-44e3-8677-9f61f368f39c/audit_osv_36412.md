# [C] ksmbd: fix use-after-free of share_conf in compound request

## Summary
Severity: Critical
Advisory: CVE-2026-23428
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23428
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.4.0 <6.12.78, >=6.7.0 <6.18.20, >=6.13.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free of share_conf in compound request

smb2_get_ksmbd_tcon() reuses work->tcon in compound requests without
validating tcon->t_state. ksmbd_tree_conn_lookup() checks t_state ==
TREE_CONNECTED on the initial lookup path, but the compound reuse path
bypasses this check entirely.

If a prior command in the compound (SMB2_TREE_DISCONNECT) sets t_state
to TREE_DISCONNECTED and frees share_conf via ksmbd_share_config_put(),
subsequent commands dereference the freed share_conf through
work->tcon->share_conf.

KASAN report:

[    4.144653] ==================================================================
[    4.145059] BUG: KASAN: slab-use-after-free in smb2_write+0xc74/0xe70
[    4.145415] Read of size 4 at addr ffff88810430c194 by task kworker/1:1/44
[    4.145772]
[    4.145867] CPU: 1 UID: 0 PID: 44 Comm: kworker/1:1 Not tainted 7.0.0-rc3+ #60 PREEMPTLAZY
[    4.145871] Hardware name: QEMU Ubuntu 24.04 PC v2 (i440FX + PIIX, arch_caps fix, 1996), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
[    4.145875] Workqueue: ksmbd-io handle_ksmbd_work
[    4.145888] Call Trace:
[    4.145892]  <TASK>
[    4.145894]  dump_stack_lvl+0x64/0x80
[    4.145910]  print_report+0xce/0x660
[    4.145919]  ? __pfx__raw_spin_lock_irqsave+0x10/0x10
[    4.145928]  ? smb2_write+0xc74/0xe70
[    4.145931]  kasan_report+0xce/0x100
[    4.145934]  ? smb2_write+0xc74/0xe70
[    4.145937]  smb2_write+0xc74/0xe70
[    4.145939]  ? __pfx_smb2_write+0x10/0x10
[    4.145942]  ? _raw_spin_unlock+0xe/0x30
[    4.145945]  ? ksmbd_smb2_check_message+0xeb2/0x24c0
[    4.145948]  ? smb2_tree_disconnect+0x31c/0x480
[    4.145951]  handle_ksmbd_work+0x40f/0x1080
[    4.145953]  process_one_work+0x5fa/0xef0
[    4.145962]  ? assign_work+0x122/0x3e0
[    4.145964]  worker_thread+0x54b/0xf70
[    4.145967]  ? __pfx_worker_thread+0x10/0x10
[    4.145970]  kthread+0x346/0x470
[    4.145976]  ? recalc_sigpending+0x19b/0x230
[    4.145980]  ? __pfx_kthread+0x10/0x10
[    4.145984]  ret_from_fork+0x4fb/0x6c0
[    4.145992]  ? __pfx_ret_from_fork+0x10/0x10
[    4.145995]  ? __switch_to+0x36c/0xbe0
[    4.145999]  ? __pfx_kthread+0x10/0x10
[    4.146003]  ret_from_fork_asm+0x1a/0x30
[    4.146013]  </TASK>
[    4.146014]
[    4.149858] Allocated by task 44:
[    4.149953]  kasan_save_stack+0x33/0x60
[    4.150061]  kasan_save_track+0x14/0x30
[    4.150169]  __kasan_kmalloc+0x8f/0xa0
[    4.150274]  ksmbd_share_config_get+0x1dd/0xdd0
[    4.150401]  ksmbd_tree_conn_connect+0x7e/0x600
[    4.150529]  smb2_tree_connect+0x2e6/0x1000
[    4.150645]  handle_ksmbd_work+0x40f/0x1080
[    4.150761]  process_one_work+0x5fa/0xef0
[    4.150873]  worker_thread+0x54b/0xf70
[    4.150978]  kthread+0x346/0x470
[    4.151071]  ret_from_fork+0x4fb/0x6c0
[    4.151176]  ret_from_fork_asm+0x1a/0x30
[    4.151286]
[    4.151332] Freed by task 44:
[    4.151418]  kasan_save_stack+0x33/0x60
[    4.151526]  kasan_save_track+0x14/0x30
[    4.151634]  kasan_save_free_info+0x3b/0x60
[    4.151751]  __kasan_slab_free+0x43/0x70
[    4.151861]  kfree+0x1ca/0x430
[    4.151952]  __ksmbd_tree_conn_disconnect+0xc8/0x190
[    4.152088]  smb2_tree_disconnect+0x1cd/0x480
[    4.152211]  handle_ksmbd_work+0x40f/0x1080
[    4.152326]  process_one_work+0x5fa/0xef0
[    4.152438]  worker_thread+0x54b/0xf70
[    4.152545]  kthread+0x346/0x470
[    4.152638]  ret_from_fork+0x4fb/0x6c0
[    4.152743]  ret_from_fork_asm+0x1a/0x30
[    4.152853]
[    4.152900] The buggy address belongs to the object at ffff88810430c180
[    4.152900]  which belongs to the cache kmalloc-96 of size 96
[    4.153226] The buggy address is located 20 bytes inside of
[    4.153226]  freed 96-byte region [ffff88810430c180, ffff88810430c1e0)
[    4.153549]
[    4.153596] The buggy address belongs to the physical page:
[    4.153750] page: refcount:0 mapcount:0 mapping:0000000000000000 index:0xffff88810430ce80 pfn:0x10430c
[    4.154000] flags: 0x
---truncated---

## References
- https://git.kernel.org/stable/c/7f7468fd2a7554cea91b7d430335a3dbf01dcc09
- https://git.kernel.org/stable/c/806f13752652216db0c309392b4db3e64eeed4f2
- https://git.kernel.org/stable/c/a5929c2020ce54e1dcbd1078c0f30b8aaf73c105
- https://git.kernel.org/stable/c/c33615f995aee80657b9fdfbc4ee7f49c2bd733d
- https://git.kernel.org/stable/c/c742b46a153d3ff95ff0825ab1950c87b9e14470
- https://git.kernel.org/stable/c/d08417981155883068b7260d9500ca306a03edac
- https://git.kernel.org/stable/c/eae0dc86f71e6f3294c0cd7ffc05039258d243af
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23428.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23428
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
