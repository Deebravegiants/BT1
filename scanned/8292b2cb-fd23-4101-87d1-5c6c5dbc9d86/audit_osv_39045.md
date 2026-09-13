# [H] bonding: fix type confusion in bond_setup_by_slave()

## Summary
Severity: High
Advisory: CVE-2026-43456
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43456
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <6.6.145, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bonding: fix type confusion in bond_setup_by_slave()

kernel BUG at net/core/skbuff.c:2306!
Oops: invalid opcode: 0000 [#1] SMP KASAN NOPTI
RIP: 0010:pskb_expand_head+0xa08/0xfe0 net/core/skbuff.c:2306
RSP: 0018:ffffc90004aff760 EFLAGS: 00010293
RAX: 0000000000000000 RBX: ffff88807e3c8780 RCX: ffffffff89593e0e
RDX: ffff88807b7c4900 RSI: ffffffff89594747 RDI: ffff88807b7c4900
RBP: 0000000000000820 R08: 0000000000000005 R09: 0000000000000000
R10: 00000000961a63e0 R11: 0000000000000000 R12: ffff88807e3c8780
R13: 00000000961a6560 R14: dffffc0000000000 R15: 00000000961a63e0
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 00007fe1a0ed8df0 CR3: 000000002d816000 CR4: 00000000003526f0
Call Trace:
 <TASK>
 ipgre_header+0xdd/0x540 net/ipv4/ip_gre.c:900
 dev_hard_header include/linux/netdevice.h:3439 [inline]
 packet_snd net/packet/af_packet.c:3028 [inline]
 packet_sendmsg+0x3ae5/0x53c0 net/packet/af_packet.c:3108
 sock_sendmsg_nosec net/socket.c:727 [inline]
 __sock_sendmsg net/socket.c:742 [inline]
 ____sys_sendmsg+0xa54/0xc30 net/socket.c:2592
 ___sys_sendmsg+0x190/0x1e0 net/socket.c:2646
 __sys_sendmsg+0x170/0x220 net/socket.c:2678
 do_syscall_x64 arch/x86/entry/syscall_64.c:63 [inline]
 do_syscall_64+0x106/0xf80 arch/x86/entry/syscall_64.c:94
 entry_SYSCALL_64_after_hwframe+0x77/0x7f
RIP: 0033:0x7fe1a0e6c1a9

When a non-Ethernet device (e.g. GRE tunnel) is enslaved to a bond,
bond_setup_by_slave() directly copies the slave's header_ops to the
bond device:

    bond_dev->header_ops = slave_dev->header_ops;

This causes a type confusion when dev_hard_header() is later called
on the bond device. Functions like ipgre_header(), ip6gre_header(),all use
netdev_priv(dev) to access their device-specific private data. When
called with the bond device, netdev_priv() returns the bond's private
data (struct bonding) instead of the expected type (e.g. struct
ip_tunnel), leading to garbage values being read and kernel crashes.

Fix this by introducing bond_header_ops with wrapper functions that
delegate to the active slave's header_ops using the slave's own
device. This ensures netdev_priv() in the slave's header functions
always receives the correct device.

The fix is placed in the bonding driver rather than individual device
drivers, as the root cause is bond blindly inheriting header_ops from
the slave without considering that these callbacks expect a specific
netdev_priv() layout.

The type confusion can be observed by adding a printk in
ipgre_header() and running the following commands:

    ip link add dummy0 type dummy
    ip addr add 10.0.0.1/24 dev dummy0
    ip link set dummy0 up
    ip link add gre1 type gre local 10.0.0.1
    ip link add bond1 type bond mode active-backup
    ip link set gre1 master bond1
    ip link set gre1 up
    ip link set bond1 up
    ip addr add fe80::1/64 dev bond1

## References
- https://git.kernel.org/stable/c/5d0fb9806ab6cf2c3cfba0e1b8c701da65e25af8
- https://git.kernel.org/stable/c/6ac890f1d60ac3707ee8dae15a67d9a833e49956
- https://git.kernel.org/stable/c/950803f7254721c1c15858fbbfae3deaaeeecb11
- https://git.kernel.org/stable/c/95597d11dc8bddb2b9a051c9232000bfbb5e43ba
- https://git.kernel.org/stable/c/9baf26a91565b7bb2b1d9f99aaf884a2b28c2f6d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43456.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43456
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
