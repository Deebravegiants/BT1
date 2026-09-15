# [M] CVE-2021-47612

## Summary
Severity: Medium
Advisory: CVE-2021-47612
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47612
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: fix segfault in nfc_genl_dump_devices_done

When kmalloc in nfc_genl_dump_devices() fails then
nfc_genl_dump_devices_done() segfaults as below

KASAN: null-ptr-deref in range [0x0000000000000008-0x000000000000000f]
CPU: 0 PID: 25 Comm: kworker/0:1 Not tainted 5.16.0-rc4-01180-g2a987e65025e-dirty #5
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.14.0-6.fc35 04/01/2014
Workqueue: events netlink_sock_destruct_work
RIP: 0010:klist_iter_exit+0x26/0x80
Call Trace:
<TASK>
class_dev_iter_exit+0x15/0x20
nfc_genl_dump_devices_done+0x3b/0x50
genl_lock_done+0x84/0xd0
netlink_sock_destruct+0x8f/0x270
__sk_destruct+0x64/0x3b0
sk_destruct+0xa8/0xd0
__sk_free+0x2e8/0x3d0
sk_free+0x51/0x90
netlink_sock_destruct_work+0x1c/0x20
process_one_work+0x411/0x710
worker_thread+0x6fd/0xa80

## References
- https://git.kernel.org/stable/c/c602863ad28ec86794cb4ab4edea5324f555f181
- https://git.kernel.org/stable/c/d731ecc6f2eaec68f4ad1542283bbc7d07bd0112
- https://git.kernel.org/stable/c/d89e4211b51752daf063d638af50abed2fd5f96d
- https://git.kernel.org/stable/c/ea55b3797878752aa076b118afb727dcf79cac34
- https://git.kernel.org/stable/c/fd79a0cbf0b2e34bcc45b13acf962e2032a82203
- https://git.kernel.org/stable/c/214af18abbe39db05beb305b2d11e87d09a6529c
- https://git.kernel.org/stable/c/2a8845b9603c545fddd17862282dc4c4ce0971e3
- https://git.kernel.org/stable/c/6644989642844de830f9b072cd65c553cb55946c
