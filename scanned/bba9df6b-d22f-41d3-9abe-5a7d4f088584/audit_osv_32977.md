# [H] net: vlan: fix VLAN 0 refcount imbalance of toggling filtering during runtime

## Summary
Severity: High
Advisory: CVE-2025-38470
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-38470
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: vlan: fix VLAN 0 refcount imbalance of toggling filtering during runtime

Assuming the "rx-vlan-filter" feature is enabled on a net device, the
8021q module will automatically add or remove VLAN 0 when the net device
is put administratively up or down, respectively. There are a couple of
problems with the above scheme.

The first problem is a memory leak that can happen if the "rx-vlan-filter"
feature is disabled while the device is running:

 # ip link add bond1 up type bond mode 0
 # ethtool -K bond1 rx-vlan-filter off
 # ip link del dev bond1

When the device is put administratively down the "rx-vlan-filter"
feature is disabled, so the 8021q module will not remove VLAN 0 and the
memory will be leaked [1].

Another problem that can happen is that the kernel can automatically
delete VLAN 0 when the device is put administratively down despite not
adding it when the device was put administratively up since during that
time the "rx-vlan-filter" feature was disabled. null-ptr-unref or
bug_on[2] will be triggered by unregister_vlan_dev() for refcount
imbalance if toggling filtering during runtime:

$ ip link add bond0 type bond mode 0
$ ip link add link bond0 name vlan0 type vlan id 0 protocol 802.1q
$ ethtool -K bond0 rx-vlan-filter off
$ ifconfig bond0 up
$ ethtool -K bond0 rx-vlan-filter on
$ ifconfig bond0 down
$ ip link del vlan0

Root cause is as below:
step1: add vlan0 for real_dev, such as bond, team.
register_vlan_dev
    vlan_vid_add(real_dev,htons(ETH_P_8021Q),0) //refcnt=1
step2: disable vlan filter feature and enable real_dev
step3: change filter from 0 to 1
vlan_device_event
    vlan_filter_push_vids
        ndo_vlan_rx_add_vid //No refcnt added to real_dev vlan0
step4: real_dev down
vlan_device_event
    vlan_vid_del(dev, htons(ETH_P_8021Q), 0); //refcnt=0
        vlan_info_rcu_free //free vlan0
step5: delete vlan0
unregister_vlan_dev
    BUG_ON(!vlan_info); //vlan_info is null

Fix both problems by noting in the VLAN info whether VLAN 0 was
automatically added upon NETDEV_UP and based on that decide whether it
should be deleted upon NETDEV_DOWN, regardless of the state of the
"rx-vlan-filter" feature.

[1]
unreferenced object 0xffff8880068e3100 (size 256):
  comm "ip", pid 384, jiffies 4296130254
  hex dump (first 32 bytes):
    00 20 30 0d 80 88 ff ff 00 00 00 00 00 00 00 00  . 0.............
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace (crc 81ce31fa):
    __kmalloc_cache_noprof+0x2b5/0x340
    vlan_vid_add+0x434/0x940
    vlan_device_event.cold+0x75/0xa8
    notifier_call_chain+0xca/0x150
    __dev_notify_flags+0xe3/0x250
    rtnl_configure_link+0x193/0x260
    rtnl_newlink_create+0x383/0x8e0
    __rtnl_newlink+0x22c/0xa40
    rtnl_newlink+0x627/0xb00
    rtnetlink_rcv_msg+0x6fb/0xb70
    netlink_rcv_skb+0x11f/0x350
    netlink_unicast+0x426/0x710
    netlink_sendmsg+0x75a/0xc20
    __sock_sendmsg+0xc1/0x150
    ____sys_sendmsg+0x5aa/0x7b0
    ___sys_sendmsg+0xfc/0x180

[2]
kernel BUG at net/8021q/vlan.c:99!
Oops: invalid opcode: 0000 [#1] SMP KASAN PTI
CPU: 0 UID: 0 PID: 382 Comm: ip Not tainted 6.16.0-rc3 #61 PREEMPT(voluntary)
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996),
BIOS rel-1.13.0-0-gf21b5a4aeb02-prebuilt.qemu.org 04/01/2014
RIP: 0010:unregister_vlan_dev (net/8021q/vlan.c:99 (discriminator 1))
RSP: 0018:ffff88810badf310 EFLAGS: 00010246
RAX: 0000000000000000 RBX: ffff88810da84000 RCX: ffffffffb47ceb9a
RDX: dffffc0000000000 RSI: 0000000000000008 RDI: ffff88810e8b43c8
RBP: 0000000000000000 R08: 0000000000000000 R09: fffffbfff6cefe80
R10: ffffffffb677f407 R11: ffff88810badf3c0 R12: ffff88810e8b4000
R13: 0000000000000000 R14: ffff88810642a5c0 R15: 000000000000017e
FS:  00007f1ff68c20c0(0000) GS:ffff888163a24000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 00007f1ff5dad240 CR3: 0000000107e56000 CR4: 00000000000006f0
Call Trace:
 <TASK
---truncated---

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/047b61a24d7c866c502aeeea482892969a68f216
- https://git.kernel.org/stable/c/35142b3816832889e50164d993018ea5810955ae
- https://git.kernel.org/stable/c/579d4f9ca9a9a605184a9b162355f6ba131f678d
- https://git.kernel.org/stable/c/8984bcbd1edf5bee5be06ad771d157333b790c33
- https://git.kernel.org/stable/c/93715aa2d80e6c5cea1bb486321fc4585076928b
- https://git.kernel.org/stable/c/ba48d3993af23753e1f1f01c8d592de9c7785f24
- https://git.kernel.org/stable/c/bb515c41306454937464da055609b5fb0a27821b
- https://git.kernel.org/stable/c/d43ef15bf4856c8c4c6c3572922331a5f06deb77
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38470.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38470
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
