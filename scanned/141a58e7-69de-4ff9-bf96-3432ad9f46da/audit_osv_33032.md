# [H] Bluetooth: hci_devcd_dump: fix out-of-bounds via dev_coredumpv

## Summary
Severity: High
Advisory: CVE-2025-38592
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38592
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_devcd_dump: fix out-of-bounds via dev_coredumpv

Currently both dev_coredumpv and skb_put_data in hci_devcd_dump use
hdev->dump.head. However, dev_coredumpv can free the buffer. From
dev_coredumpm_timeout documentation, which is used by dev_coredumpv:

    > Creates a new device coredump for the given device. If a previous one hasn't
    > been read yet, the new coredump is discarded. The data lifetime is determined
    > by the device coredump framework and when it is no longer needed the @free
    > function will be called to free the data.

If the data has not been read by the userspace yet, dev_coredumpv will
discard new buffer, freeing hdev->dump.head. This leads to
vmalloc-out-of-bounds error when skb_put_data tries to access
hdev->dump.head.

A crash report from syzbot illustrates this:

    ==================================================================
    BUG: KASAN: vmalloc-out-of-bounds in skb_put_data
    include/linux/skbuff.h:2752 [inline]
    BUG: KASAN: vmalloc-out-of-bounds in hci_devcd_dump+0x142/0x240
    net/bluetooth/coredump.c:258
    Read of size 140 at addr ffffc90004ed5000 by task kworker/u9:2/5844

    CPU: 1 UID: 0 PID: 5844 Comm: kworker/u9:2 Not tainted
    6.14.0-syzkaller-10892-g4e82c87058f4 #0 PREEMPT(full)
    Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS
    Google 02/12/2025
    Workqueue: hci0 hci_devcd_timeout
    Call Trace:
     <TASK>
     __dump_stack lib/dump_stack.c:94 [inline]
     dump_stack_lvl+0x116/0x1f0 lib/dump_stack.c:120
     print_address_description mm/kasan/report.c:408 [inline]
     print_report+0xc3/0x670 mm/kasan/report.c:521
     kasan_report+0xe0/0x110 mm/kasan/report.c:634
     check_region_inline mm/kasan/generic.c:183 [inline]
     kasan_check_range+0xef/0x1a0 mm/kasan/generic.c:189
     __asan_memcpy+0x23/0x60 mm/kasan/shadow.c:105
     skb_put_data include/linux/skbuff.h:2752 [inline]
     hci_devcd_dump+0x142/0x240 net/bluetooth/coredump.c:258
     hci_devcd_timeout+0xb5/0x2e0 net/bluetooth/coredump.c:413
     process_one_work+0x9cc/0x1b70 kernel/workqueue.c:3238
     process_scheduled_works kernel/workqueue.c:3319 [inline]
     worker_thread+0x6c8/0xf10 kernel/workqueue.c:3400
     kthread+0x3c2/0x780 kernel/kthread.c:464
     ret_from_fork+0x45/0x80 arch/x86/kernel/process.c:153
     ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:245
     </TASK>

    The buggy address ffffc90004ed5000 belongs to a vmalloc virtual mapping
    Memory state around the buggy address:
     ffffc90004ed4f00: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8
     ffffc90004ed4f80: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8
    >ffffc90004ed5000: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8
                       ^
     ffffc90004ed5080: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8
     ffffc90004ed5100: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8
    ==================================================================

To avoid this issue, reorder dev_coredumpv to be called after
skb_put_data that does not free the data.

## References
- https://git.kernel.org/stable/c/7af4d7b53502286c6cf946d397ab183e76d14820
- https://git.kernel.org/stable/c/8c021ad797f9171d015cf0a932a3fbe5232190f5
- https://git.kernel.org/stable/c/efd55f6a59449f8d4e4953f12c177aa902b7451f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38592.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38592
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
