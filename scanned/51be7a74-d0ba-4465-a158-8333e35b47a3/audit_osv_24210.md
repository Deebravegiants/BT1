# [H] Bluetooth: hci_sysfs: Fix attempting to call device_add multiple times

## Summary
Severity: High
Advisory: CVE-2022-50419
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50419
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <4.9.331, >=4.10.0 <4.14.296, >=4.15.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sysfs: Fix attempting to call device_add multiple times

device_add shall not be called multiple times as stated in its
documentation:

 'Do not call this routine or device_register() more than once for
 any device structure'

Syzkaller reports a bug as follows [1]:
------------[ cut here ]------------
kernel BUG at lib/list_debug.c:33!
invalid opcode: 0000 [#1] PREEMPT SMP KASAN
[...]
Call Trace:
 <TASK>
 __list_add include/linux/list.h:69 [inline]
 list_add_tail include/linux/list.h:102 [inline]
 kobj_kset_join lib/kobject.c:164 [inline]
 kobject_add_internal+0x18f/0x8f0 lib/kobject.c:214
 kobject_add_varg lib/kobject.c:358 [inline]
 kobject_add+0x150/0x1c0 lib/kobject.c:410
 device_add+0x368/0x1e90 drivers/base/core.c:3452
 hci_conn_add_sysfs+0x9b/0x1b0 net/bluetooth/hci_sysfs.c:53
 hci_le_cis_estabilished_evt+0x57c/0xae0 net/bluetooth/hci_event.c:6799
 hci_le_meta_evt+0x2b8/0x510 net/bluetooth/hci_event.c:7110
 hci_event_func net/bluetooth/hci_event.c:7440 [inline]
 hci_event_packet+0x63d/0xfd0 net/bluetooth/hci_event.c:7495
 hci_rx_work+0xae7/0x1230 net/bluetooth/hci_core.c:4007
 process_one_work+0x991/0x1610 kernel/workqueue.c:2289
 worker_thread+0x665/0x1080 kernel/workqueue.c:2436
 kthread+0x2e4/0x3a0 kernel/kthread.c:376
 ret_from_fork+0x1f/0x30 arch/x86/entry/entry_64.S:306
 </TASK>

## References
- https://git.kernel.org/stable/c/1b6c89571f453101251201f0fad1c26f7256e937
- https://git.kernel.org/stable/c/3423a50fa018e88aed4c900d59c3c8334d8ad583
- https://git.kernel.org/stable/c/448a496f760664d3e2e79466aa1787e6abc922b5
- https://git.kernel.org/stable/c/4bcefec3636208b4c97536b26014d5935d5c10a0
- https://git.kernel.org/stable/c/6144423712d570247b8ca26e50a277c30dd13702
- https://git.kernel.org/stable/c/671fee73e08ff415d36a7c16bdf238927df83884
- https://git.kernel.org/stable/c/6e85d2ad958c6f034b1b158d904019869dbb3c81
- https://git.kernel.org/stable/c/7b674dce4162bb46d396586e30e4653427023875
- https://git.kernel.org/stable/c/ef055094df4c10b73cfe67c8d43f9de1fb608a8b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50419.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50419
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
