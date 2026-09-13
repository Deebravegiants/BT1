# [H] netfilter: x_tables: fix LED ID check in led_tg_check()

## Summary
Severity: High
Advisory: CVE-2024-56650
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56650
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: x_tables: fix LED ID check in led_tg_check()

Syzbot has reported the following BUG detected by KASAN:

BUG: KASAN: slab-out-of-bounds in strlen+0x58/0x70
Read of size 1 at addr ffff8881022da0c8 by task repro/5879
...
Call Trace:
 <TASK>
 dump_stack_lvl+0x241/0x360
 ? __pfx_dump_stack_lvl+0x10/0x10
 ? __pfx__printk+0x10/0x10
 ? _printk+0xd5/0x120
 ? __virt_addr_valid+0x183/0x530
 ? __virt_addr_valid+0x183/0x530
 print_report+0x169/0x550
 ? __virt_addr_valid+0x183/0x530
 ? __virt_addr_valid+0x183/0x530
 ? __virt_addr_valid+0x45f/0x530
 ? __phys_addr+0xba/0x170
 ? strlen+0x58/0x70
 kasan_report+0x143/0x180
 ? strlen+0x58/0x70
 strlen+0x58/0x70
 kstrdup+0x20/0x80
 led_tg_check+0x18b/0x3c0
 xt_check_target+0x3bb/0xa40
 ? __pfx_xt_check_target+0x10/0x10
 ? stack_depot_save_flags+0x6e4/0x830
 ? nft_target_init+0x174/0xc30
 nft_target_init+0x82d/0xc30
 ? __pfx_nft_target_init+0x10/0x10
 ? nf_tables_newrule+0x1609/0x2980
 ? nf_tables_newrule+0x1609/0x2980
 ? rcu_is_watching+0x15/0xb0
 ? nf_tables_newrule+0x1609/0x2980
 ? nf_tables_newrule+0x1609/0x2980
 ? __kmalloc_noprof+0x21a/0x400
 nf_tables_newrule+0x1860/0x2980
 ? __pfx_nf_tables_newrule+0x10/0x10
 ? __nla_parse+0x40/0x60
 nfnetlink_rcv+0x14e5/0x2ab0
 ? __pfx_validate_chain+0x10/0x10
 ? __pfx_nfnetlink_rcv+0x10/0x10
 ? __lock_acquire+0x1384/0x2050
 ? netlink_deliver_tap+0x2e/0x1b0
 ? __pfx_lock_release+0x10/0x10
 ? netlink_deliver_tap+0x2e/0x1b0
 netlink_unicast+0x7f8/0x990
 ? __pfx_netlink_unicast+0x10/0x10
 ? __virt_addr_valid+0x183/0x530
 ? __check_object_size+0x48e/0x900
 netlink_sendmsg+0x8e4/0xcb0
 ? __pfx_netlink_sendmsg+0x10/0x10
 ? aa_sock_msg_perm+0x91/0x160
 ? __pfx_netlink_sendmsg+0x10/0x10
 __sock_sendmsg+0x223/0x270
 ____sys_sendmsg+0x52a/0x7e0
 ? __pfx_____sys_sendmsg+0x10/0x10
 __sys_sendmsg+0x292/0x380
 ? __pfx___sys_sendmsg+0x10/0x10
 ? lockdep_hardirqs_on_prepare+0x43d/0x780
 ? __pfx_lockdep_hardirqs_on_prepare+0x10/0x10
 ? exc_page_fault+0x590/0x8c0
 ? do_syscall_64+0xb6/0x230
 do_syscall_64+0xf3/0x230
 entry_SYSCALL_64_after_hwframe+0x77/0x7f
...
 </TASK>

Since an invalid (without '\0' byte at all) byte sequence may be passed
from userspace, add an extra check to ensure that such a sequence is
rejected as possible ID and so never passed to 'kstrdup()' and further.

## References
- https://git.kernel.org/stable/c/04317f4eb2aad312ad85c1a17ad81fe75f1f9bc7
- https://git.kernel.org/stable/c/147a42bb02de8735cb08476be6d0917987d022c2
- https://git.kernel.org/stable/c/36a9d94dac28beef6b8abba46ba8874320d3e800
- https://git.kernel.org/stable/c/a9bcc0b70d9baf3ff005874489a0dc9d023b54c3
- https://git.kernel.org/stable/c/ab9916321c95f5280b72b4c5055e269f98627efe
- https://git.kernel.org/stable/c/ad28612ebae1fcc1104bd432e99e99d87f6bfe09
- https://git.kernel.org/stable/c/c40c96d98e536fc1daaa125c2332b988615e30a4
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56650.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56650
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
