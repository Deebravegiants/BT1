# [H] wifi: mt7601u: fix an integer underflow

## Summary
Severity: High
Advisory: CVE-2023-53679
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53679
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt7601u: fix an integer underflow

Fix an integer underflow that leads to a null pointer dereference in
'mt7601u_rx_skb_from_seg()'. The variable 'dma_len' in the URB packet
could be manipulated, which could trigger an integer underflow of
'seg_len' in 'mt7601u_rx_process_seg()'. This underflow subsequently
causes the 'bad_frame' checks in 'mt7601u_rx_skb_from_seg()' to be
bypassed, eventually leading to a dereference of the pointer 'p', which
is a null pointer.

Ensure that 'dma_len' is greater than 'min_seg_len'.

Found by a modified version of syzkaller.

KASAN: null-ptr-deref in range [0x0000000000000008-0x000000000000000f]
CPU: 0 PID: 12 Comm: ksoftirqd/0 Tainted: G        W  O      5.14.0+
#139
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS
rel-1.12.1-0-ga5cab58e9a3f-prebuilt.qemu.org 04/01/2014
RIP: 0010:skb_add_rx_frag+0x143/0x370
Code: e2 07 83 c2 03 38 ca 7c 08 84 c9 0f 85 86 01 00 00 4c 8d 7d 08 44
89 68 08 48 b8 00 00 00 00 00 fc ff df 4c 89 fa 48 c1 ea 03 <80> 3c 02
00 0f 85 cd 01 00 00 48 8b 45 08 a8 01 0f 85 3d 01 00 00
RSP: 0018:ffffc900000cfc90 EFLAGS: 00010202
RAX: dffffc0000000000 RBX: ffff888115520dc0 RCX: 0000000000000000
RDX: 0000000000000001 RSI: ffff8881118430c0 RDI: ffff8881118430f8
RBP: 0000000000000000 R08: 0000000000000e09 R09: 0000000000000010
R10: ffff888111843017 R11: ffffed1022308602 R12: 0000000000000000
R13: 0000000000000e09 R14: 0000000000000010 R15: 0000000000000008
FS:  0000000000000000(0000) GS:ffff88811a800000(0000)
knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 000000004035af40 CR3: 00000001157f2000 CR4: 0000000000750ef0
DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
PKRU: 55555554
Call Trace:
 mt7601u_rx_tasklet+0xc73/0x1270
 ? mt7601u_submit_rx_buf.isra.0+0x510/0x510
 ? tasklet_action_common.isra.0+0x79/0x2f0
 tasklet_action_common.isra.0+0x206/0x2f0
 __do_softirq+0x1b5/0x880
 ? tasklet_unlock+0x30/0x30
 run_ksoftirqd+0x26/0x50
 smpboot_thread_fn+0x34f/0x7d0
 ? smpboot_register_percpu_thread+0x370/0x370
 kthread+0x3a1/0x480
 ? set_kthread_struct+0x120/0x120
 ret_from_fork+0x1f/0x30
Modules linked in: 88XXau(O) 88x2bu(O)
---[ end trace 57f34f93b4da0f9b ]---
RIP: 0010:skb_add_rx_frag+0x143/0x370
Code: e2 07 83 c2 03 38 ca 7c 08 84 c9 0f 85 86 01 00 00 4c 8d 7d 08 44
89 68 08 48 b8 00 00 00 00 00 fc ff df 4c 89 fa 48 c1 ea 03 <80> 3c 02
00 0f 85 cd 01 00 00 48 8b 45 08 a8 01 0f 85 3d 01 00 00
RSP: 0018:ffffc900000cfc90 EFLAGS: 00010202
RAX: dffffc0000000000 RBX: ffff888115520dc0 RCX: 0000000000000000
RDX: 0000000000000001 RSI: ffff8881118430c0 RDI: ffff8881118430f8
RBP: 0000000000000000 R08: 0000000000000e09 R09: 0000000000000010
R10: ffff888111843017 R11: ffffed1022308602 R12: 0000000000000000
R13: 0000000000000e09 R14: 0000000000000010 R15: 0000000000000008
FS:  0000000000000000(0000) GS:ffff88811a800000(0000)
knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 000000004035af40 CR3: 00000001157f2000 CR4: 0000000000750ef0
DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
PKRU: 55555554

## References
- https://git.kernel.org/stable/c/1a1f43059afae5cc9409e0c3bc63bfc09bc8facb
- https://git.kernel.org/stable/c/47dc1f425af57b71111d7b01ebd24e04e8d967ef
- https://git.kernel.org/stable/c/61d0163e2be7a439cf6f82e9ad7de563ecf41e7a
- https://git.kernel.org/stable/c/67e4519afba215199b6dfa39ce5d7ea673ee4138
- https://git.kernel.org/stable/c/803f3176c5df3b5582c27ea690f204abb60b19b9
- https://git.kernel.org/stable/c/d0db59e2f718d1e2f1d2a2d8092168fdd2f3add0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53679.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53679
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
