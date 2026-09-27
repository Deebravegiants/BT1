# [H] media: rc: fix races with imon_disconnect()

## Summary
Severity: High
Advisory: CVE-2025-39993
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39993
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.110, >=6.7.0 <6.12.51, >=6.13.0 <6.16.11, >=6.17.0 <6.17.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: rc: fix races with imon_disconnect()

Syzbot reports a KASAN issue as below:
BUG: KASAN: use-after-free in __create_pipe include/linux/usb.h:1945 [inline]
BUG: KASAN: use-after-free in send_packet+0xa2d/0xbc0 drivers/media/rc/imon.c:627
Read of size 4 at addr ffff8880256fb000 by task syz-executor314/4465

CPU: 2 PID: 4465 Comm: syz-executor314 Not tainted 6.0.0-rc1-syzkaller #0
Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.14.0-2 04/01/2014
Call Trace:
 <TASK>
__dump_stack lib/dump_stack.c:88 [inline]
dump_stack_lvl+0xcd/0x134 lib/dump_stack.c:106
print_address_description mm/kasan/report.c:317 [inline]
print_report.cold+0x2ba/0x6e9 mm/kasan/report.c:433
kasan_report+0xb1/0x1e0 mm/kasan/report.c:495
__create_pipe include/linux/usb.h:1945 [inline]
send_packet+0xa2d/0xbc0 drivers/media/rc/imon.c:627
vfd_write+0x2d9/0x550 drivers/media/rc/imon.c:991
vfs_write+0x2d7/0xdd0 fs/read_write.c:576
ksys_write+0x127/0x250 fs/read_write.c:631
do_syscall_x64 arch/x86/entry/common.c:50 [inline]
do_syscall_64+0x35/0xb0 arch/x86/entry/common.c:80
entry_SYSCALL_64_after_hwframe+0x63/0xcd

The iMON driver improperly releases the usb_device reference in
imon_disconnect without coordinating with active users of the
device.

Specifically, the fields usbdev_intf0 and usbdev_intf1 are not
protected by the users counter (ictx->users). During probe,
imon_init_intf0 or imon_init_intf1 increments the usb_device
reference count depending on the interface. However, during
disconnect, usb_put_dev is called unconditionally, regardless of
actual usage.

As a result, if vfd_write or other operations are still in
progress after disconnect, this can lead to a use-after-free of
the usb_device pointer.

Thread 1 vfd_write                      Thread 2 imon_disconnect
                                        ...
                                        if
                                          usb_put_dev(ictx->usbdev_intf0)
                                        else
                                          usb_put_dev(ictx->usbdev_intf1)
...
while
  send_packet
    if
      pipe = usb_sndintpipe(
        ictx->usbdev_intf0) UAF
    else
      pipe = usb_sndctrlpipe(
        ictx->usbdev_intf0, 0) UAF

Guard access to usbdev_intf0 and usbdev_intf1 after disconnect by
checking ictx->disconnected in all writer paths. Add early return
with -ENODEV in send_packet(), vfd_write(), lcd_write() and
display_open() if the device is no longer present.

Set and read ictx->disconnected under ictx->lock to ensure memory
synchronization. Acquire the lock in imon_disconnect() before setting
the flag to synchronize with any ongoing operations.

Ensure writers exit early and safely after disconnect before the USB
core proceeds with cleanup.

Found by Linux Verification Center (linuxtesting.org) with Syzkaller.

## References
- https://git.kernel.org/stable/c/2e7fd93b9cc565b839bc55a6662475718963e156
- https://git.kernel.org/stable/c/71096a6161a25e84acddb89a9d77f138502d26ab
- https://git.kernel.org/stable/c/71c52b073922d05e79e6de7fc7f5f38f927929a4
- https://git.kernel.org/stable/c/71da40648741d15b302700b68973fe8b382aef3c
- https://git.kernel.org/stable/c/9348976003e39754af344949579e824a0a210fc4
- https://git.kernel.org/stable/c/b03fac6e2a38331faf8510b480becfa90cea1c9f
- https://git.kernel.org/stable/c/d9f6ce99624a41c3bcb29a8d7d79b800665229dd
- https://git.kernel.org/stable/c/fa0f61cc1d828178aa921475a9b786e7fbb65ccb
- https://git.kernel.org/stable/c/fd5d3e6b149ec8cce045d86a2b5e3664d6b32ba5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39993.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39993
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
