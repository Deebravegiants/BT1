# [H] nbd: call genl_unregister_family() first in nbd_cleanup()

## Summary
Severity: High
Advisory: CVE-2022-49295
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49295
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nbd: call genl_unregister_family() first in nbd_cleanup()

Otherwise there may be race between module removal and the handling of
netlink command, which can lead to the oops as shown below:

  BUG: kernel NULL pointer dereference, address: 0000000000000098
  Oops: 0002 [#1] SMP PTI
  CPU: 1 PID: 31299 Comm: nbd-client Tainted: G            E     5.14.0-rc4
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)
  RIP: 0010:down_write+0x1a/0x50
  Call Trace:
   start_creating+0x89/0x130
   debugfs_create_dir+0x1b/0x130
   nbd_start_device+0x13d/0x390 [nbd]
   nbd_genl_connect+0x42f/0x748 [nbd]
   genl_family_rcv_msg_doit.isra.0+0xec/0x150
   genl_rcv_msg+0xe5/0x1e0
   netlink_rcv_skb+0x55/0x100
   genl_rcv+0x29/0x40
   netlink_unicast+0x1a8/0x250
   netlink_sendmsg+0x21b/0x430
   ____sys_sendmsg+0x2a4/0x2d0
   ___sys_sendmsg+0x81/0xc0
   __sys_sendmsg+0x62/0xb0
   __x64_sys_sendmsg+0x1f/0x30
   do_syscall_64+0x3b/0xc0
   entry_SYSCALL_64_after_hwframe+0x44/0xae
  Modules linked in: nbd(E-)

## References
- https://git.kernel.org/stable/c/013a79f1b5c89290e2e97f1ebf14b14e0cf5fe5c
- https://git.kernel.org/stable/c/06c4da89c24e7023ea448cadf8e9daf06a0aae6e
- https://git.kernel.org/stable/c/1be608e1ee1f222464b2856bda9b85ab5184a33e
- https://git.kernel.org/stable/c/3d5da1ffba3388c2ae2e6c598855a4d887d3bf79
- https://git.kernel.org/stable/c/6f505bbb8063fd3a238a4239d2d8c165e5279f6f
- https://git.kernel.org/stable/c/8a1435c862ea09b06be7acda325128dc08458e25
- https://git.kernel.org/stable/c/c0868f6e728c3c28bef0e8bee89d2daf86a8bbca
- https://git.kernel.org/stable/c/cbeafa7a79d08ecdb55f8f1d41a11323d0f709db
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49295.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49295
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
