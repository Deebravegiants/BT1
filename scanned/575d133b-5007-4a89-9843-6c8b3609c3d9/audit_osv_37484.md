# [H] wifi: virt_wifi: remove SET_NETDEV_DEV to avoid use-after-free

## Summary
Severity: High
Advisory: CVE-2026-31695
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31695
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: virt_wifi: remove SET_NETDEV_DEV to avoid use-after-free

Currently we execute `SET_NETDEV_DEV(dev, &priv->lowerdev->dev)` for
the virt_wifi net devices. However, unregistering a virt_wifi device in
netdev_run_todo() can happen together with the device referenced by
SET_NETDEV_DEV().

It can result in use-after-free during the ethtool operations performed
on a virt_wifi device that is currently being unregistered. Such a net
device can have the `dev.parent` field pointing to the freed memory,
but ethnl_ops_begin() calls `pm_runtime_get_sync(dev->dev.parent)`.

Let's remove SET_NETDEV_DEV for virt_wifi to avoid bugs like this:

 ==================================================================
 BUG: KASAN: slab-use-after-free in __pm_runtime_resume+0xe2/0xf0
 Read of size 2 at addr ffff88810cfc46f8 by task pm/606

 Call Trace:
  <TASK>
  dump_stack_lvl+0x4d/0x70
  print_report+0x170/0x4f3
  ? __pfx__raw_spin_lock_irqsave+0x10/0x10
  kasan_report+0xda/0x110
  ? __pm_runtime_resume+0xe2/0xf0
  ? __pm_runtime_resume+0xe2/0xf0
  __pm_runtime_resume+0xe2/0xf0
  ethnl_ops_begin+0x49/0x270
  ethnl_set_features+0x23c/0xab0
  ? __pfx_ethnl_set_features+0x10/0x10
  ? kvm_sched_clock_read+0x11/0x20
  ? local_clock_noinstr+0xf/0xf0
  ? local_clock+0x10/0x30
  ? kasan_save_track+0x25/0x60
  ? __kasan_kmalloc+0x7f/0x90
  ? genl_family_rcv_msg_attrs_parse.isra.0+0x150/0x2c0
  genl_family_rcv_msg_doit+0x1e7/0x2c0
  ? __pfx_genl_family_rcv_msg_doit+0x10/0x10
  ? __pfx_cred_has_capability.isra.0+0x10/0x10
  ? stack_trace_save+0x8e/0xc0
  genl_rcv_msg+0x411/0x660
  ? __pfx_genl_rcv_msg+0x10/0x10
  ? __pfx_ethnl_set_features+0x10/0x10
  netlink_rcv_skb+0x121/0x380
  ? __pfx_genl_rcv_msg+0x10/0x10
  ? __pfx_netlink_rcv_skb+0x10/0x10
  ? __pfx_down_read+0x10/0x10
  genl_rcv+0x23/0x30
  netlink_unicast+0x60f/0x830
  ? __pfx_netlink_unicast+0x10/0x10
  ? __pfx___alloc_skb+0x10/0x10
  netlink_sendmsg+0x6ea/0xbc0
  ? __pfx_netlink_sendmsg+0x10/0x10
  ? __futex_queue+0x10b/0x1f0
  ____sys_sendmsg+0x7a2/0x950
  ? copy_msghdr_from_user+0x26b/0x430
  ? __pfx_____sys_sendmsg+0x10/0x10
  ? __pfx_copy_msghdr_from_user+0x10/0x10
  ___sys_sendmsg+0xf8/0x180
  ? __pfx____sys_sendmsg+0x10/0x10
  ? __pfx_futex_wait+0x10/0x10
  ? fdget+0x2e4/0x4a0
  __sys_sendmsg+0x11f/0x1c0
  ? __pfx___sys_sendmsg+0x10/0x10
  do_syscall_64+0xe2/0x570
  ? exc_page_fault+0x66/0xb0
  entry_SYSCALL_64_after_hwframe+0x77/0x7f
  </TASK>

This fix may be combined with another one in the ethtool subsystem:
https://lore.kernel.org/all/20260322075917.254874-1-alex.popov@linux.com/T/#u

## References
- https://git.kernel.org/stable/c/5adc01506da94dfaab76f3d1b8410a8ca7bfc59d
- https://git.kernel.org/stable/c/5bbadf60b121065ffb267ec92018607b9c1c7524
- https://git.kernel.org/stable/c/789b06f9f39cdc7e895bdab2c034e39c41c8f8d6
- https://git.kernel.org/stable/c/c5fa98842783ed227365d1303785de6a67020c8d
- https://git.kernel.org/stable/c/d1e3aa80e6e04410ba89eaaba4441a0d749d181d
- https://git.kernel.org/stable/c/dcb5915696bd7b32b6404a897c24ee47cb23e772
- https://git.kernel.org/stable/c/e90f3e74e1ebc26c461a74be490d322716bcdcb4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31695.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31695
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
