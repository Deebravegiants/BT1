# [M] gtp: Suppress list corruption splat in gtp_net_exit_batch_rtnl().

## Summary
Severity: Medium
Advisory: CVE-2025-21865
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21865
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.130, >=6.2.0 <6.6.80, >=6.7.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

gtp: Suppress list corruption splat in gtp_net_exit_batch_rtnl().

Brad Spengler reported the list_del() corruption splat in
gtp_net_exit_batch_rtnl(). [0]

Commit eb28fd76c0a0 ("gtp: Destroy device along with udp socket's netns
dismantle.") added the for_each_netdev() loop in gtp_net_exit_batch_rtnl()
to destroy devices in each netns as done in geneve and ip tunnels.

However, this could trigger ->dellink() twice for the same device during
->exit_batch_rtnl().

Say we have two netns A & B and gtp device B that resides in netns B but
whose UDP socket is in netns A.

  1. cleanup_net() processes netns A and then B.

  2. gtp_net_exit_batch_rtnl() finds the device B while iterating
     netns A's gn->gtp_dev_list and calls ->dellink().

  [ device B is not yet unlinked from netns B
    as unregister_netdevice_many() has not been called. ]

  3. gtp_net_exit_batch_rtnl() finds the device B while iterating
     netns B's for_each_netdev() and calls ->dellink().

gtp_dellink() cleans up the device's hash table, unlinks the dev from
gn->gtp_dev_list, and calls unregister_netdevice_queue().

Basically, calling gtp_dellink() multiple times is fine unless
CONFIG_DEBUG_LIST is enabled.

Let's remove for_each_netdev() in gtp_net_exit_batch_rtnl() and
delegate the destruction to default_device_exit_batch() as done
in bareudp.

[0]:
list_del corruption, ffff8880aaa62c00->next (autoslab_size_M_dev_P_net_core_dev_11127_8_1328_8_S_4096_A_64_n_139+0xc00/0x1000 [slab object]) is LIST_POISON1 (ffffffffffffff02) (prev is 0xffffffffffffff04)
kernel BUG at lib/list_debug.c:58!
Oops: invalid opcode: 0000 [#1] PREEMPT SMP KASAN
CPU: 1 UID: 0 PID: 1804 Comm: kworker/u8:7 Tainted: G                T   6.12.13-grsec-full-20250211091339 #1
Tainted: [T]=RANDSTRUCT
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.15.0-1 04/01/2014
Workqueue: netns cleanup_net
RIP: 0010:[<ffffffff84947381>] __list_del_entry_valid_or_report+0x141/0x200 lib/list_debug.c:58
Code: c2 76 91 31 c0 e8 9f b1 f7 fc 0f 0b 4d 89 f0 48 c7 c1 02 ff ff ff 48 89 ea 48 89 ee 48 c7 c7 e0 c2 76 91 31 c0 e8 7f b1 f7 fc <0f> 0b 4d 89 e8 48 c7 c1 04 ff ff ff 48 89 ea 48 89 ee 48 c7 c7 60
RSP: 0018:fffffe8040b4fbd0 EFLAGS: 00010283
RAX: 00000000000000cc RBX: dffffc0000000000 RCX: ffffffff818c4054
RDX: ffffffff84947381 RSI: ffffffff818d1512 RDI: 0000000000000000
RBP: ffff8880aaa62c00 R08: 0000000000000001 R09: fffffbd008169f32
R10: fffffe8040b4f997 R11: 0000000000000001 R12: a1988d84f24943e4
R13: ffffffffffffff02 R14: ffffffffffffff04 R15: ffff8880aaa62c08
RBX: kasan shadow of 0x0
RCX: __wake_up_klogd.part.0+0x74/0xe0 kernel/printk/printk.c:4554
RDX: __list_del_entry_valid_or_report+0x141/0x200 lib/list_debug.c:58
RSI: vprintk+0x72/0x100 kernel/printk/printk_safe.c:71
RBP: autoslab_size_M_dev_P_net_core_dev_11127_8_1328_8_S_4096_A_64_n_139+0xc00/0x1000 [slab object]
RSP: process kstack fffffe8040b4fbd0+0x7bd0/0x8000 [kworker/u8:7+netns 1804 ]
R09: kasan shadow of process kstack fffffe8040b4f990+0x7990/0x8000 [kworker/u8:7+netns 1804 ]
R10: process kstack fffffe8040b4f997+0x7997/0x8000 [kworker/u8:7+netns 1804 ]
R15: autoslab_size_M_dev_P_net_core_dev_11127_8_1328_8_S_4096_A_64_n_139+0xc08/0x1000 [slab object]
FS:  0000000000000000(0000) GS:ffff888116000000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 0000748f5372c000 CR3: 0000000015408000 CR4: 00000000003406f0 shadow CR4: 00000000003406f0
Stack:
 0000000000000000 ffffffff8a0c35e7 ffffffff8a0c3603 ffff8880aaa62c00
 ffff8880aaa62c00 0000000000000004 ffff88811145311c 0000000000000005
 0000000000000001 ffff8880aaa62000 fffffe8040b4fd40 ffffffff8a0c360d
Call Trace:
 <TASK>
 [<ffffffff8a0c360d>] __list_del_entry_valid include/linux/list.h:131 [inline] fffffe8040b4fc28
 [<ffffffff8a0c360d>] __list_del_entry include/linux/list.h:248 [inline] fffffe8040b4fc28
 [<ffffffff8a0c360d>] list_del include/linux/list.h:262 [inl
---truncated---

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/33eb925c0c26e86ca540a08254806512bf911f22
- https://git.kernel.org/stable/c/37e7644b961600ef0beb01d3970c3034a62913af
- https://git.kernel.org/stable/c/4ccacf86491d33d2486b62d4d44864d7101b299d
- https://git.kernel.org/stable/c/7f86fb07db65a470d0c11f79da551bd9466357dc
- https://git.kernel.org/stable/c/9d03e7e37187ae140e716377599493987fb20c5b
- https://git.kernel.org/stable/c/b70fa591b066d52b141fc430ffdee35b6cc87a66
- https://git.kernel.org/stable/c/cb15bb1bde0ba97cbbed9508e45210dcafec3657
- https://git.kernel.org/stable/c/ff81b14010362f6188ca26fec22ff05e4da45595
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21865.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21865
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
