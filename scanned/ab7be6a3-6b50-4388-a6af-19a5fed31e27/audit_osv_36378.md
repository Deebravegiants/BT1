# [H] macvlan: observe an RCU grace period in macvlan_common_newlink() error path

## Summary
Severity: High
Advisory: CVE-2026-23273
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-23273
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

macvlan: observe an RCU grace period in macvlan_common_newlink() error path

valis reported that a race condition still happens after my prior patch.

macvlan_common_newlink() might have made @dev visible before
detecting an error, and its caller will directly call free_netdev(dev).

We must respect an RCU period, either in macvlan or the core networking
stack.

After adding a temporary mdelay(1000) in macvlan_forward_source_one()
to open the race window, valis repro was:

ip link add p1 type veth peer p2
ip link set address 00:00:00:00:00:20 dev p1
ip link set up dev p1
ip link set up dev p2
ip link add mv0 link p2 type macvlan mode source

(ip link add invalid% link p2 type macvlan mode source macaddr add
00:00:00:00:00:20 &) ; sleep 0.5 ; ping -c1 -I p1 1.2.3.4
PING 1.2.3.4 (1.2.3.4): 56 data bytes
RTNETLINK answers: Invalid argument

BUG: KASAN: slab-use-after-free in macvlan_forward_source
(drivers/net/macvlan.c:408 drivers/net/macvlan.c:444)
Read of size 8 at addr ffff888016bb89c0 by task e/175

CPU: 1 UID: 1000 PID: 175 Comm: e Not tainted 6.19.0-rc8+ #33 NONE
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.14.0-2 04/01/2014
Call Trace:
<IRQ>
dump_stack_lvl (lib/dump_stack.c:123)
print_report (mm/kasan/report.c:379 mm/kasan/report.c:482)
? macvlan_forward_source (drivers/net/macvlan.c:408 drivers/net/macvlan.c:444)
kasan_report (mm/kasan/report.c:597)
? macvlan_forward_source (drivers/net/macvlan.c:408 drivers/net/macvlan.c:444)
macvlan_forward_source (drivers/net/macvlan.c:408 drivers/net/macvlan.c:444)
? tasklet_init (kernel/softirq.c:983)
macvlan_handle_frame (drivers/net/macvlan.c:501)

Allocated by task 169:
kasan_save_stack (mm/kasan/common.c:58)
kasan_save_track (./arch/x86/include/asm/current.h:25
mm/kasan/common.c:70 mm/kasan/common.c:79)
__kasan_kmalloc (mm/kasan/common.c:419)
__kvmalloc_node_noprof (./include/linux/kasan.h:263 mm/slub.c:5657
mm/slub.c:7140)
alloc_netdev_mqs (net/core/dev.c:12012)
rtnl_create_link (net/core/rtnetlink.c:3648)
rtnl_newlink (net/core/rtnetlink.c:3830 net/core/rtnetlink.c:3957
net/core/rtnetlink.c:4072)
rtnetlink_rcv_msg (net/core/rtnetlink.c:6958)
netlink_rcv_skb (net/netlink/af_netlink.c:2550)
netlink_unicast (net/netlink/af_netlink.c:1319 net/netlink/af_netlink.c:1344)
netlink_sendmsg (net/netlink/af_netlink.c:1894)
__sys_sendto (net/socket.c:727 net/socket.c:742 net/socket.c:2206)
__x64_sys_sendto (net/socket.c:2209)
do_syscall_64 (arch/x86/entry/syscall_64.c:63 arch/x86/entry/syscall_64.c:94)
entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:131)

Freed by task 169:
kasan_save_stack (mm/kasan/common.c:58)
kasan_save_track (./arch/x86/include/asm/current.h:25
mm/kasan/common.c:70 mm/kasan/common.c:79)
kasan_save_free_info (mm/kasan/generic.c:587)
__kasan_slab_free (mm/kasan/common.c:287)
kfree (mm/slub.c:6674 mm/slub.c:6882)
rtnl_newlink (net/core/rtnetlink.c:3845 net/core/rtnetlink.c:3957
net/core/rtnetlink.c:4072)
rtnetlink_rcv_msg (net/core/rtnetlink.c:6958)
netlink_rcv_skb (net/netlink/af_netlink.c:2550)
netlink_unicast (net/netlink/af_netlink.c:1319 net/netlink/af_netlink.c:1344)
netlink_sendmsg (net/netlink/af_netlink.c:1894)
__sys_sendto (net/socket.c:727 net/socket.c:742 net/socket.c:2206)
__x64_sys_sendto (net/socket.c:2209)
do_syscall_64 (arch/x86/entry/syscall_64.c:63 arch/x86/entry/syscall_64.c:94)
entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:131)

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/19c7d8ac51988d053709c1e85bd8482076af845d
- https://git.kernel.org/stable/c/1e58ae87ad1e6e24368dea9aec9048c758cd0e2b
- https://git.kernel.org/stable/c/3d94323c80d7fc4da5f10f9bb06a45d39d5d3cc4
- https://git.kernel.org/stable/c/721eb342d9ba19bad5c4815ea3921465158b7362
- https://git.kernel.org/stable/c/91e4ff8d966978901630fc29582c1a76d3c6e46c
- https://git.kernel.org/stable/c/a1f686d273d129b45712d95f4095843b864466bd
- https://git.kernel.org/stable/c/d34f7a8aa9a25b7e64e0e46e444697c0f702374d
- https://git.kernel.org/stable/c/e3f000f0dee1bfab52e2e61ca6a3835d9e187e35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23273.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23273
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
