# [H] NFC: NULL out the dev->rfkill to prevent UAF

## Summary
Severity: High
Advisory: CVE-2022-49505
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49505
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFC: NULL out the dev->rfkill to prevent UAF

Commit 3e3b5dfcd16a ("NFC: reorder the logic in nfc_{un,}register_device")
assumes the device_is_registered() in function nfc_dev_up() will help
to check when the rfkill is unregistered. However, this check only
take effect when device_del(&dev->dev) is done in nfc_unregister_device().
Hence, the rfkill object is still possible be dereferenced.

The crash trace in latest kernel (5.18-rc2):

[   68.760105] ==================================================================
[   68.760330] BUG: KASAN: use-after-free in __lock_acquire+0x3ec1/0x6750
[   68.760756] Read of size 8 at addr ffff888009c93018 by task fuzz/313
[   68.760756]
[   68.760756] CPU: 0 PID: 313 Comm: fuzz Not tainted 5.18.0-rc2 #4
[   68.760756] Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS rel-1.14.0-0-g155821a1990b-prebuilt.qemu.org 04/01/2014
[   68.760756] Call Trace:
[   68.760756]  <TASK>
[   68.760756]  dump_stack_lvl+0x57/0x7d
[   68.760756]  print_report.cold+0x5e/0x5db
[   68.760756]  ? __lock_acquire+0x3ec1/0x6750
[   68.760756]  kasan_report+0xbe/0x1c0
[   68.760756]  ? __lock_acquire+0x3ec1/0x6750
[   68.760756]  __lock_acquire+0x3ec1/0x6750
[   68.760756]  ? lockdep_hardirqs_on_prepare+0x410/0x410
[   68.760756]  ? register_lock_class+0x18d0/0x18d0
[   68.760756]  lock_acquire+0x1ac/0x4f0
[   68.760756]  ? rfkill_blocked+0xe/0x60
[   68.760756]  ? lockdep_hardirqs_on_prepare+0x410/0x410
[   68.760756]  ? mutex_lock_io_nested+0x12c0/0x12c0
[   68.760756]  ? nla_get_range_signed+0x540/0x540
[   68.760756]  ? _raw_spin_lock_irqsave+0x4e/0x50
[   68.760756]  _raw_spin_lock_irqsave+0x39/0x50
[   68.760756]  ? rfkill_blocked+0xe/0x60
[   68.760756]  rfkill_blocked+0xe/0x60
[   68.760756]  nfc_dev_up+0x84/0x260
[   68.760756]  nfc_genl_dev_up+0x90/0xe0
[   68.760756]  genl_family_rcv_msg_doit+0x1f4/0x2f0
[   68.760756]  ? genl_family_rcv_msg_attrs_parse.constprop.0+0x230/0x230
[   68.760756]  ? security_capable+0x51/0x90
[   68.760756]  genl_rcv_msg+0x280/0x500
[   68.760756]  ? genl_get_cmd+0x3c0/0x3c0
[   68.760756]  ? lock_acquire+0x1ac/0x4f0
[   68.760756]  ? nfc_genl_dev_down+0xe0/0xe0
[   68.760756]  ? lockdep_hardirqs_on_prepare+0x410/0x410
[   68.760756]  netlink_rcv_skb+0x11b/0x340
[   68.760756]  ? genl_get_cmd+0x3c0/0x3c0
[   68.760756]  ? netlink_ack+0x9c0/0x9c0
[   68.760756]  ? netlink_deliver_tap+0x136/0xb00
[   68.760756]  genl_rcv+0x1f/0x30
[   68.760756]  netlink_unicast+0x430/0x710
[   68.760756]  ? memset+0x20/0x40
[   68.760756]  ? netlink_attachskb+0x740/0x740
[   68.760756]  ? __build_skb_around+0x1f4/0x2a0
[   68.760756]  netlink_sendmsg+0x75d/0xc00
[   68.760756]  ? netlink_unicast+0x710/0x710
[   68.760756]  ? netlink_unicast+0x710/0x710
[   68.760756]  sock_sendmsg+0xdf/0x110
[   68.760756]  __sys_sendto+0x19e/0x270
[   68.760756]  ? __ia32_sys_getpeername+0xa0/0xa0
[   68.760756]  ? fd_install+0x178/0x4c0
[   68.760756]  ? fd_install+0x195/0x4c0
[   68.760756]  ? kernel_fpu_begin_mask+0x1c0/0x1c0
[   68.760756]  __x64_sys_sendto+0xd8/0x1b0
[   68.760756]  ? lockdep_hardirqs_on+0xbf/0x130
[   68.760756]  ? syscall_enter_from_user_mode+0x1d/0x50
[   68.760756]  do_syscall_64+0x3b/0x90
[   68.760756]  entry_SYSCALL_64_after_hwframe+0x44/0xae
[   68.760756] RIP: 0033:0x7f67fb50e6b3
...
[   68.760756] RSP: 002b:00007f67fa91fe90 EFLAGS: 00000293 ORIG_RAX: 000000000000002c
[   68.760756] RAX: ffffffffffffffda RBX: 0000000000000000 RCX: 00007f67fb50e6b3
[   68.760756] RDX: 000000000000001c RSI: 0000559354603090 RDI: 0000000000000003
[   68.760756] RBP: 00007f67fa91ff00 R08: 00007f67fa91fedc R09: 000000000000000c
[   68.760756] R10: 0000000000000000 R11: 0000000000000293 R12: 00007ffe824d496e
[   68.760756] R13: 00007ffe824d496f R14: 00007f67fa120000 R15: 0000000000000003

[   68.760756]  </TASK>
[   68.760756]
[   68.760756] Allocated by task 279:
[   68.760756]  kasan_save_stack+0x1e/0x40
[
---truncated---

## References
- https://git.kernel.org/stable/c/1632be63862f183cd5cf1cc094e698e6ec005dfd
- https://git.kernel.org/stable/c/1b0e81416a24d6e9b8c2341e22e8bf48f8b8bfc9
- https://git.kernel.org/stable/c/2a1b5110c95e4d49c8c3906270dfcde680a5a7be
- https://git.kernel.org/stable/c/4a68938f43b7c2663e4c90bb9bbe29ac8b9a42a0
- https://git.kernel.org/stable/c/4f5d71930f41be78557f9714393179025baacd65
- https://git.kernel.org/stable/c/6abfaca8711803d0d7cc8c0fac1070a88509d463
- https://git.kernel.org/stable/c/a8e03bcad52dc9afabf650fdbad84f739cec9efa
- https://git.kernel.org/stable/c/f81270125b50532624400063281e6611ecd61ddf
- https://git.kernel.org/stable/c/fbf9c4c714d3cdeb98b6a18e4d057f931cad1d81
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49505.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49505
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
