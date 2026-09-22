# [H] bonding: alb: re-check primary_is_promisc under RTNL in bond_alb_monitor

## Summary
Severity: High
Advisory: CVE-2026-74726
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74726
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bonding: alb: re-check primary_is_promisc under RTNL in bond_alb_monitor

bond_alb_monitor() reads primary_is_promisc under RCU, then drops RCU and
takes RTNL via rtnl_trylock() before undoing the promiscuity it set on the
active slave. In that window the active slave can change under RTNL
(RTM_DELLINK -> __bond_release_one() -> bond_alb_handle_active_change()),
which already drops the promiscuity and clears primary_is_promisc. The
monitor still acts on the stale decision: if the slave was removed with no
failover, curr_active_slave is now NULL and the deref faults; if it failed
over, the stale dev_set_promiscuity(-1) underflows the new slave's
promiscuity counter and pins it in IFF_PROMISC.

  Oops: general protection fault, probably for non-canonical address ...
  KASAN: null-ptr-deref in range [0x0000000000000000-0x0000000000000007]
  Workqueue: b42 bond_alb_monitor
  RIP: 0010:bond_alb_monitor (drivers/net/bonding/bond_alb.c:1600)
   process_one_work (kernel/workqueue.c:3322)
   worker_thread (kernel/workqueue.c:3486)
   kthread (kernel/kthread.c:436)
   ret_from_fork (arch/x86/kernel/process.c:158)
  Kernel panic - not syncing: Fatal exception

Re-check primary_is_promisc (and curr_active_slave) after taking RTNL so
the monitor only undoes an increment it still owns. The other bonding
monitors already re-read state under RTNL in their commit phase
(bond_miimon_commit/bond_ab_arp_commit); bond_alb_monitor() was the only
one acting on the pre-trylock decision.

## References
- https://git.kernel.org/stable/c/09add8d5cfa9c46828f51eaad162c36e86366b71
- https://git.kernel.org/stable/c/257c4a3a34d8f51efb00f35375a0c6ce3c8f6ce2
- https://git.kernel.org/stable/c/2faf75a8a06504071b4c0aea7e45a9cc49a4e187
- https://git.kernel.org/stable/c/683c6ba6e58e6ed1037831ea97dd58d9c0e76b8d
- https://git.kernel.org/stable/c/b82f51681a7a88c7d3c865e817a3340d42b5fa2a
- https://git.kernel.org/stable/c/dccec0227ed8d9e36936d66e256b957dc2858468
- https://git.kernel.org/stable/c/dd148539fb4741d01c06b7d2c8bd84b01920756c
- https://git.kernel.org/stable/c/f7668762bf5fd6db9397de5c0514407489d9d815
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74726.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74726
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
