# [M] Bluetooth: L2CAP: Fix memory leak in vhci_write

## Summary
Severity: Medium
Advisory: CVE-2022-49908
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49908
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: Fix memory leak in vhci_write

Syzkaller reports a memory leak as follows:
====================================
BUG: memory leak
unreferenced object 0xffff88810d81ac00 (size 240):
  [...]
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace:
    [<ffffffff838733d9>] __alloc_skb+0x1f9/0x270 net/core/skbuff.c:418
    [<ffffffff833f742f>] alloc_skb include/linux/skbuff.h:1257 [inline]
    [<ffffffff833f742f>] bt_skb_alloc include/net/bluetooth/bluetooth.h:469 [inline]
    [<ffffffff833f742f>] vhci_get_user drivers/bluetooth/hci_vhci.c:391 [inline]
    [<ffffffff833f742f>] vhci_write+0x5f/0x230 drivers/bluetooth/hci_vhci.c:511
    [<ffffffff815e398d>] call_write_iter include/linux/fs.h:2192 [inline]
    [<ffffffff815e398d>] new_sync_write fs/read_write.c:491 [inline]
    [<ffffffff815e398d>] vfs_write+0x42d/0x540 fs/read_write.c:578
    [<ffffffff815e3cdd>] ksys_write+0x9d/0x160 fs/read_write.c:631
    [<ffffffff845e0645>] do_syscall_x64 arch/x86/entry/common.c:50 [inline]
    [<ffffffff845e0645>] do_syscall_64+0x35/0xb0 arch/x86/entry/common.c:80
    [<ffffffff84600087>] entry_SYSCALL_64_after_hwframe+0x63/0xcd
====================================

HCI core will uses hci_rx_work() to process frame, which is queued to
the hdev->rx_q tail in hci_recv_frame() by HCI driver.

Yet the problem is that, HCI core may not free the skb after handling
ACL data packets. To be more specific, when start fragment does not
contain the L2CAP length, HCI core just copies skb into conn->rx_skb and
finishes frame process in l2cap_recv_acldata(), without freeing the skb,
which triggers the above memory leak.

This patch solves it by releasing the relative skb, after processing
the above case in l2cap_recv_acldata().

## References
- https://git.kernel.org/stable/c/5b4f039a2f487c5edae681d763fe1af505f84c13
- https://git.kernel.org/stable/c/7c9524d929648935bac2bbb4c20437df8f9c3f42
- https://git.kernel.org/stable/c/aa16cac06b752e5f609c106735bd7838f444784c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49908.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49908
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
