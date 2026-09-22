# [H] pps: Fix a use-after-free

## Summary
Severity: High
Advisory: CVE-2024-57979
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57979
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

pps: Fix a use-after-free

On a board running ntpd and gpsd, I'm seeing a consistent use-after-free
in sys_exit() from gpsd when rebooting:

    pps pps1: removed
    ------------[ cut here ]------------
    kobject: '(null)' (00000000db4bec24): is not initialized, yet kobject_put() is being called.
    WARNING: CPU: 2 PID: 440 at lib/kobject.c:734 kobject_put+0x120/0x150
    CPU: 2 UID: 299 PID: 440 Comm: gpsd Not tainted 6.11.0-rc6-00308-gb31c44928842 #1
    Hardware name: Raspberry Pi 4 Model B Rev 1.1 (DT)
    pstate: 60000005 (nZCv daif -PAN -UAO -TCO -DIT -SSBS BTYPE=--)
    pc : kobject_put+0x120/0x150
    lr : kobject_put+0x120/0x150
    sp : ffffffc0803d3ae0
    x29: ffffffc0803d3ae0 x28: ffffff8042dc9738 x27: 0000000000000001
    x26: 0000000000000000 x25: ffffff8042dc9040 x24: ffffff8042dc9440
    x23: ffffff80402a4620 x22: ffffff8042ef4bd0 x21: ffffff80405cb600
    x20: 000000000008001b x19: ffffff8040b3b6e0 x18: 0000000000000000
    x17: 0000000000000000 x16: 0000000000000000 x15: 696e6920746f6e20
    x14: 7369203a29343263 x13: 205d303434542020 x12: 0000000000000000
    x11: 0000000000000000 x10: 0000000000000000 x9 : 0000000000000000
    x8 : 0000000000000000 x7 : 0000000000000000 x6 : 0000000000000000
    x5 : 0000000000000000 x4 : 0000000000000000 x3 : 0000000000000000
    x2 : 0000000000000000 x1 : 0000000000000000 x0 : 0000000000000000
    Call trace:
     kobject_put+0x120/0x150
     cdev_put+0x20/0x3c
     __fput+0x2c4/0x2d8
     ____fput+0x1c/0x38
     task_work_run+0x70/0xfc
     do_exit+0x2a0/0x924
     do_group_exit+0x34/0x90
     get_signal+0x7fc/0x8c0
     do_signal+0x128/0x13b4
     do_notify_resume+0xdc/0x160
     el0_svc+0xd4/0xf8
     el0t_64_sync_handler+0x140/0x14c
     el0t_64_sync+0x190/0x194
    ---[ end trace 0000000000000000 ]---

...followed by more symptoms of corruption, with similar stacks:

    refcount_t: underflow; use-after-free.
    kernel BUG at lib/list_debug.c:62!
    Kernel panic - not syncing: Oops - BUG: Fatal exception

This happens because pps_device_destruct() frees the pps_device with the
embedded cdev immediately after calling cdev_del(), but, as the comment
above cdev_del() notes, fops for previously opened cdevs are still
callable even after cdev_del() returns. I think this bug has always
been there: I can't explain why it suddenly started happening every time
I reboot this particular board.

In commit d953e0e837e6 ("pps: Fix a use-after free bug when
unregistering a source."), George Spelvin suggested removing the
embedded cdev. That seems like the simplest way to fix this, so I've
implemented his suggestion, using __register_chrdev() with pps_idr
becoming the source of truth for which minor corresponds to which
device.

But now that pps_idr defines userspace visibility instead of cdev_add(),
we need to be sure the pps->dev refcount can't reach zero while
userspace can still find it again. So, the idr_remove() call moves to
pps_unregister_cdev(), and pps_idr now holds a reference to pps->dev.

    pps_core: source serial1 got cdev (251:1)
    <...>
    pps pps1: removed
    pps_core: unregistering pps1
    pps_core: deallocating pps1

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/1a7735ab2cb9747518a7416fb5929e85442dec62
- https://git.kernel.org/stable/c/785c78ed0d39d1717cca3ef931d3e51337b5e90e
- https://git.kernel.org/stable/c/7e5ee3281dc09014367f5112b6d566ba36ea2d49
- https://git.kernel.org/stable/c/85241f7de216f8298f6e48540ea13d7dcd100870
- https://git.kernel.org/stable/c/91932db1d96b2952299ce30c1c693d834d10ace6
- https://git.kernel.org/stable/c/c4041b6b0a7a3def8cf3f3d6120ff337bc4c40f7
- https://git.kernel.org/stable/c/c79a39dc8d060b9e64e8b0fa9d245d44befeefbe
- https://git.kernel.org/stable/c/cd3bbcb6b3a7caa5ce67de76723b6d8531fb7f64
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57979.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57979
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
