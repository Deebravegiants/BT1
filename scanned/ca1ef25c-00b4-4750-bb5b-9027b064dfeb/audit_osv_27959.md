# [M] media: pvrusb2: fix uaf in pvr2_context_set_notify

## Summary
Severity: Medium
Advisory: CVE-2024-26875
Ecosystem: Linux
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26875
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: pvrusb2: fix uaf in pvr2_context_set_notify

[Syzbot reported]
BUG: KASAN: slab-use-after-free in pvr2_context_set_notify+0x2c4/0x310 drivers/media/usb/pvrusb2/pvrusb2-context.c:35
Read of size 4 at addr ffff888113aeb0d8 by task kworker/1:1/26

CPU: 1 PID: 26 Comm: kworker/1:1 Not tainted 6.8.0-rc1-syzkaller-00046-gf1a27f081c1f #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 01/25/2024
Workqueue: usb_hub_wq hub_event
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0xd9/0x1b0 lib/dump_stack.c:106
 print_address_description mm/kasan/report.c:377 [inline]
 print_report+0xc4/0x620 mm/kasan/report.c:488
 kasan_report+0xda/0x110 mm/kasan/report.c:601
 pvr2_context_set_notify+0x2c4/0x310 drivers/media/usb/pvrusb2/pvrusb2-context.c:35
 pvr2_context_notify drivers/media/usb/pvrusb2/pvrusb2-context.c:95 [inline]
 pvr2_context_disconnect+0x94/0xb0 drivers/media/usb/pvrusb2/pvrusb2-context.c:272

Freed by task 906:
kasan_save_stack+0x33/0x50 mm/kasan/common.c:47
kasan_save_track+0x14/0x30 mm/kasan/common.c:68
kasan_save_free_info+0x3f/0x60 mm/kasan/generic.c:640
poison_slab_object mm/kasan/common.c:241 [inline]
__kasan_slab_free+0x106/0x1b0 mm/kasan/common.c:257
kasan_slab_free include/linux/kasan.h:184 [inline]
slab_free_hook mm/slub.c:2121 [inline]
slab_free mm/slub.c:4299 [inline]
kfree+0x105/0x340 mm/slub.c:4409
pvr2_context_check drivers/media/usb/pvrusb2/pvrusb2-context.c:137 [inline]
pvr2_context_thread_func+0x69d/0x960 drivers/media/usb/pvrusb2/pvrusb2-context.c:158

[Analyze]
Task A set disconnect_flag = !0, which resulted in Task B's condition being met
and releasing mp, leading to this issue.

[Fix]
Place the disconnect_flag assignment operation after all code in pvr2_context_disconnect()
to avoid this issue.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0a0b79ea55de8514e1750884e5fec77f9fdd01ee
- https://git.kernel.org/stable/c/3a1ec89708d2e57e2712f46241282961b1a7a475
- https://git.kernel.org/stable/c/40cd818fae875c424a8335009db33c7b5a07de3a
- https://git.kernel.org/stable/c/8e60b99f6b7ccb3badeb512f5eb613ad45904592
- https://git.kernel.org/stable/c/ab896d93fd6a2cd1afeb034c3cc9226cb499209f
- https://git.kernel.org/stable/c/d29ed08964cec8b9729bc55c7bb23f679d7a18fb
- https://git.kernel.org/stable/c/eaa410e05bdf562c90b23cdf2d9327f9c4625e16
- https://git.kernel.org/stable/c/eb6e9dce979c08210ff7249e5e0eceb8991bfcd7
- https://git.kernel.org/stable/c/ed8000e1e8e9684ab6c30cf2b526c0cea039929c
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26875.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26875
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
