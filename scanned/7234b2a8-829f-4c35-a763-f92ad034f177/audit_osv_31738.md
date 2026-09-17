# [H] net: avoid race between device unregistration and ethnl ops

## Summary
Severity: High
Advisory: CVE-2025-21701
Aliases: A-392852041, ASB-A-392852041
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-13
Source: https://osv.dev/vulnerability/CVE-2025-21701
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.179, >=5.16.0 <6.6.76, >=6.2.0 <6.12.13, >=6.7.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: avoid race between device unregistration and ethnl ops

The following trace can be seen if a device is being unregistered while
its number of channels are being modified.

  DEBUG_LOCKS_WARN_ON(lock->magic != lock)
  WARNING: CPU: 3 PID: 3754 at kernel/locking/mutex.c:564 __mutex_lock+0xc8a/0x1120
  CPU: 3 UID: 0 PID: 3754 Comm: ethtool Not tainted 6.13.0-rc6+ #771
  RIP: 0010:__mutex_lock+0xc8a/0x1120
  Call Trace:
   <TASK>
   ethtool_check_max_channel+0x1ea/0x880
   ethnl_set_channels+0x3c3/0xb10
   ethnl_default_set_doit+0x306/0x650
   genl_family_rcv_msg_doit+0x1e3/0x2c0
   genl_rcv_msg+0x432/0x6f0
   netlink_rcv_skb+0x13d/0x3b0
   genl_rcv+0x28/0x40
   netlink_unicast+0x42e/0x720
   netlink_sendmsg+0x765/0xc20
   __sys_sendto+0x3ac/0x420
   __x64_sys_sendto+0xe0/0x1c0
   do_syscall_64+0x95/0x180
   entry_SYSCALL_64_after_hwframe+0x76/0x7e

This is because unregister_netdevice_many_notify might run before the
rtnl lock section of ethnl operations, eg. set_channels in the above
example. In this example the rss lock would be destroyed by the device
unregistration path before being used again, but in general running
ethnl operations while dismantle has started is not a good idea.

Fix this by denying any operation on devices being unregistered. A check
was already there in ethnl_ops_begin, but not wide enough.

Note that the same issue cannot be seen on the ioctl version
(__dev_ethtool) because the device reference is retrieved from within
the rtnl lock section there. Once dismantle started, the net device is
unlisted and no reference will be found.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/12e070eb6964b341b41677fd260af5a305316a1f
- https://git.kernel.org/stable/c/26bc6076798aa4dc83a07d0a386f9e57c94e8517
- https://git.kernel.org/stable/c/2f29127e94ae9fdc7497331003d6860e9551cdf3
- https://git.kernel.org/stable/c/4dc880245f9b529fa8f476b5553c799d2848b47b
- https://git.kernel.org/stable/c/b1cb37a31a482df3dd35a6ac166282dac47664f4
- https://git.kernel.org/stable/c/b382ab9b885cbb665e0e70a727f101c981b4edf3
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21701.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21701
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
