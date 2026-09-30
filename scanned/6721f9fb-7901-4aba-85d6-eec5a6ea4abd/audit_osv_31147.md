# [M] team: prevent adding a device which is already a team device lower

## Summary
Severity: Medium
Advisory: CVE-2024-58071
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58071
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

team: prevent adding a device which is already a team device lower

Prevent adding a device which is already a team device lower,
e.g. adding veth0 if vlan1 was already added and veth0 is a lower of
vlan1.

This is not useful in practice and can lead to recursive locking:

$ ip link add veth0 type veth peer name veth1
$ ip link set veth0 up
$ ip link set veth1 up
$ ip link add link veth0 name veth0.1 type vlan protocol 802.1Q id 1
$ ip link add team0 type team
$ ip link set veth0.1 down
$ ip link set veth0.1 master team0
team0: Port device veth0.1 added
$ ip link set veth0 down
$ ip link set veth0 master team0

============================================
WARNING: possible recursive locking detected
6.13.0-rc2-virtme-00441-ga14a429069bb #46 Not tainted
--------------------------------------------
ip/7684 is trying to acquire lock:
ffff888016848e00 (team->team_lock_key){+.+.}-{4:4}, at: team_device_event (drivers/net/team/team_core.c:2928 drivers/net/team/team_core.c:2951 drivers/net/team/team_core.c:2973)

but task is already holding lock:
ffff888016848e00 (team->team_lock_key){+.+.}-{4:4}, at: team_add_slave (drivers/net/team/team_core.c:1147 drivers/net/team/team_core.c:1977)

other info that might help us debug this:
Possible unsafe locking scenario:

CPU0
----
lock(team->team_lock_key);
lock(team->team_lock_key);

*** DEADLOCK ***

May be due to missing lock nesting notation

2 locks held by ip/7684:

stack backtrace:
CPU: 3 UID: 0 PID: 7684 Comm: ip Not tainted 6.13.0-rc2-virtme-00441-ga14a429069bb #46
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
Call Trace:
<TASK>
dump_stack_lvl (lib/dump_stack.c:122)
print_deadlock_bug.cold (kernel/locking/lockdep.c:3040)
__lock_acquire (kernel/locking/lockdep.c:3893 kernel/locking/lockdep.c:5226)
? netlink_broadcast_filtered (net/netlink/af_netlink.c:1548)
lock_acquire.part.0 (kernel/locking/lockdep.c:467 kernel/locking/lockdep.c:5851)
? team_device_event (drivers/net/team/team_core.c:2928 drivers/net/team/team_core.c:2951 drivers/net/team/team_core.c:2973)
? trace_lock_acquire (./include/trace/events/lock.h:24 (discriminator 2))
? team_device_event (drivers/net/team/team_core.c:2928 drivers/net/team/team_core.c:2951 drivers/net/team/team_core.c:2973)
? lock_acquire (kernel/locking/lockdep.c:5822)
? team_device_event (drivers/net/team/team_core.c:2928 drivers/net/team/team_core.c:2951 drivers/net/team/team_core.c:2973)
__mutex_lock (kernel/locking/mutex.c:587 kernel/locking/mutex.c:735)
? team_device_event (drivers/net/team/team_core.c:2928 drivers/net/team/team_core.c:2951 drivers/net/team/team_core.c:2973)
? team_device_event (drivers/net/team/team_core.c:2928 drivers/net/team/team_core.c:2951 drivers/net/team/team_core.c:2973)
? fib_sync_up (net/ipv4/fib_semantics.c:2167)
? team_device_event (drivers/net/team/team_core.c:2928 drivers/net/team/team_core.c:2951 drivers/net/team/team_core.c:2973)
team_device_event (drivers/net/team/team_core.c:2928 drivers/net/team/team_core.c:2951 drivers/net/team/team_core.c:2973)
notifier_call_chain (kernel/notifier.c:85)
call_netdevice_notifiers_info (net/core/dev.c:1996)
__dev_notify_flags (net/core/dev.c:8993)
? __dev_change_flags (net/core/dev.c:8975)
dev_change_flags (net/core/dev.c:9027)
vlan_device_event (net/8021q/vlan.c:85 net/8021q/vlan.c:470)
? br_device_event (net/bridge/br.c:143)
notifier_call_chain (kernel/notifier.c:85)
call_netdevice_notifiers_info (net/core/dev.c:1996)
dev_open (net/core/dev.c:1519 net/core/dev.c:1505)
team_add_slave (drivers/net/team/team_core.c:1219 drivers/net/team/team_core.c:1977)
? __pfx_team_add_slave (drivers/net/team/team_core.c:1972)
do_set_master (net/core/rtnetlink.c:2917)
do_setlink.isra.0 (net/core/rtnetlink.c:3117)

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0a7794b9ca78c8e7d001c583bf05736169de3f20
- https://git.kernel.org/stable/c/184a564e6000b41582f160a5be9a9b5aabe22ac1
- https://git.kernel.org/stable/c/1bb06f919fa5bec77ad9b6002525c3dcc5c1fd6c
- https://git.kernel.org/stable/c/3fff5da4ca2164bb4d0f1e6cd33f6eb8a0e73e50
- https://git.kernel.org/stable/c/62ff1615815d565448c37cb8a7a2a076492ec471
- https://git.kernel.org/stable/c/adff6ac889e16d97abd1e4543f533221127e978a
- https://git.kernel.org/stable/c/bd099a2fa9be983ba0e90a57a59484fe9d520ba8
- https://git.kernel.org/stable/c/d9bce1310c0e2a55888e3e08c9f69d8377b3a377
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58071.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58071
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
