# [M] ipv4: ip_tunnel: Fix suspicious RCU usage warning in ip_tunnel_init_flow()

## Summary
Severity: Medium
Advisory: CVE-2024-53042
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53042
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.229, >=5.11.0 <5.15.171, >=5.16.0 <6.1.116, >=5.18.0 <6.6.60, >=6.2.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: ip_tunnel: Fix suspicious RCU usage warning in ip_tunnel_init_flow()

There are code paths from which the function is called without holding
the RCU read lock, resulting in a suspicious RCU usage warning [1].

Fix by using l3mdev_master_upper_ifindex_by_index() which will acquire
the RCU read lock before calling
l3mdev_master_upper_ifindex_by_index_rcu().

[1]
WARNING: suspicious RCU usage
6.12.0-rc3-custom-gac8f72681cf2 #141 Not tainted
-----------------------------
net/core/dev.c:876 RCU-list traversed in non-reader section!!

other info that might help us debug this:

rcu_scheduler_active = 2, debug_locks = 1
1 lock held by ip/361:
 #0: ffffffff86fc7cb0 (rtnl_mutex){+.+.}-{3:3}, at: rtnetlink_rcv_msg+0x377/0xf60

stack backtrace:
CPU: 3 UID: 0 PID: 361 Comm: ip Not tainted 6.12.0-rc3-custom-gac8f72681cf2 #141
Hardware name: Bochs Bochs, BIOS Bochs 01/01/2011
Call Trace:
 <TASK>
 dump_stack_lvl+0xba/0x110
 lockdep_rcu_suspicious.cold+0x4f/0xd6
 dev_get_by_index_rcu+0x1d3/0x210
 l3mdev_master_upper_ifindex_by_index_rcu+0x2b/0xf0
 ip_tunnel_bind_dev+0x72f/0xa00
 ip_tunnel_newlink+0x368/0x7a0
 ipgre_newlink+0x14c/0x170
 __rtnl_newlink+0x1173/0x19c0
 rtnl_newlink+0x6c/0xa0
 rtnetlink_rcv_msg+0x3cc/0xf60
 netlink_rcv_skb+0x171/0x450
 netlink_unicast+0x539/0x7f0
 netlink_sendmsg+0x8c1/0xd80
 ____sys_sendmsg+0x8f9/0xc20
 ___sys_sendmsg+0x197/0x1e0
 __sys_sendmsg+0x122/0x1f0
 do_syscall_64+0xbb/0x1d0
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/5edcb3fdb12c3d46a6e79eeeec27d925b80fc168
- https://git.kernel.org/stable/c/699b48fc31727792edf2cab3829586ae6ba649e2
- https://git.kernel.org/stable/c/6dfaa458fe923211c766238a224e0a3c0522935c
- https://git.kernel.org/stable/c/72c0f482e39c87317ebf67661e28c8d86c93e870
- https://git.kernel.org/stable/c/ad4a3ca6a8e886f6491910a3ae5d53595e40597d
- https://git.kernel.org/stable/c/e2742758c9c85c84e077ede5f916479f724e11c2
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53042.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53042
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
