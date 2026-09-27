# [H] Bluetooth: L2CAP: Fix div-by-zero in l2cap_le_flowctl_init()

## Summary
Severity: High
Advisory: CVE-2024-36968
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-06-08
Source: https://osv.dev/vulnerability/CVE-2024-36968
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <6.6.32, >=6.7.0 <6.8.11, >=6.9.0 <6.9.2, >=6.10.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: Fix div-by-zero in l2cap_le_flowctl_init()

l2cap_le_flowctl_init() can cause both div-by-zero and an integer
overflow since hdev->le_mtu may not fall in the valid range.

Move MTU from hci_dev to hci_conn to validate MTU and stop the connection
process earlier if MTU is invalid.
Also, add a missing validation in read_buffer_size() and make it return
an error value if the validation fails.
Now hci_conn_add() returns ERR_PTR() as it can fail due to the both a
kzalloc failure and invalid MTU value.

divide error: 0000 [#1] PREEMPT SMP KASAN NOPTI
CPU: 0 PID: 67 Comm: kworker/u5:0 Tainted: G        W          6.9.0-rc5+ #20
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.15.0-1 04/01/2014
Workqueue: hci0 hci_rx_work
RIP: 0010:l2cap_le_flowctl_init+0x19e/0x3f0 net/bluetooth/l2cap_core.c:547
Code: e8 17 17 0c 00 66 41 89 9f 84 00 00 00 bf 01 00 00 00 41 b8 02 00 00 00 4c
89 fe 4c 89 e2 89 d9 e8 27 17 0c 00 44 89 f0 31 d2 <66> f7 f3 89 c3 ff c3 4d 8d
b7 88 00 00 00 4c 89 f0 48 c1 e8 03 42
RSP: 0018:ffff88810bc0f858 EFLAGS: 00010246
RAX: 00000000000002a0 RBX: 0000000000000000 RCX: dffffc0000000000
RDX: 0000000000000000 RSI: ffff88810bc0f7c0 RDI: ffffc90002dcb66f
RBP: ffff88810bc0f880 R08: aa69db2dda70ff01 R09: 0000ffaaaaaaaaaa
R10: 0084000000ffaaaa R11: 0000000000000000 R12: ffff88810d65a084
R13: dffffc0000000000 R14: 00000000000002a0 R15: ffff88810d65a000
FS:  0000000000000000(0000) GS:ffff88811ac00000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 0000000020000100 CR3: 0000000103268003 CR4: 0000000000770ef0
PKRU: 55555554
Call Trace:
 <TASK>
 l2cap_le_connect_req net/bluetooth/l2cap_core.c:4902 [inline]
 l2cap_le_sig_cmd net/bluetooth/l2cap_core.c:5420 [inline]
 l2cap_le_sig_channel net/bluetooth/l2cap_core.c:5486 [inline]
 l2cap_recv_frame+0xe59d/0x11710 net/bluetooth/l2cap_core.c:6809
 l2cap_recv_acldata+0x544/0x10a0 net/bluetooth/l2cap_core.c:7506
 hci_acldata_packet net/bluetooth/hci_core.c:3939 [inline]
 hci_rx_work+0x5e5/0xb20 net/bluetooth/hci_core.c:4176
 process_one_work kernel/workqueue.c:3254 [inline]
 process_scheduled_works+0x90f/0x1530 kernel/workqueue.c:3335
 worker_thread+0x926/0xe70 kernel/workqueue.c:3416
 kthread+0x2e3/0x380 kernel/kthread.c:388
 ret_from_fork+0x5c/0x90 arch/x86/kernel/process.c:147
 ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:244
 </TASK>
Modules linked in:
---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/4d3dbaa252257d20611c3647290e6171f1bbd6c8
- https://git.kernel.org/stable/c/a5b862c6a221459d54e494e88965b48dcfa6cc44
- https://git.kernel.org/stable/c/ad3f7986c5a0f82b8b66a0afe1cc1f5421e1d674
- https://git.kernel.org/stable/c/d2b2f7d3936dc5990549bc36ab7ac7ac37f22c30
- https://git.kernel.org/stable/c/dfece2b4e3759759b2bdfac2cd6d0ee9fbf055f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36968.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36968
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
