# [H] rds: tcp: hold the RCU lock across ipv6_chk_addr() in rds_tcp_laddr_check()

## Summary
Severity: High
Advisory: CVE-2026-74563
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74563
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

rds: tcp: hold the RCU lock across ipv6_chk_addr() in rds_tcp_laddr_check()

rds_tcp_laddr_check() looks up a scoped IPv6 interface with
dev_get_by_index_rcu(), drops the RCU read-side lock, and only then
passes the bare struct net_device * into ipv6_chk_addr().

dev_get_by_index_rcu() only keeps the device alive within the same RCU
read-side section. After rcu_read_unlock(), a concurrent RTM_DELLINK can
free the net_device; ipv6_chk_addr() then dereferences the stale pointer
in __ipv6_chk_addr_and_flags() (e.g. l3mdev_master_dev_rcu(dev)), reading
freed memory.

Keep the RCU read-side lock held across the ipv6_chk_addr() call instead
of dropping it right after the lookup, so the device cannot be freed
while it is in use.

  BUG: KASAN: slab-use-after-free in __ipv6_chk_addr_and_flags (... net/ipv6/addrconf.c:1998)
  Read of size 8 at addr ffff8880106ec000 by task exploit/153
  Call Trace:
   ...
   kasan_report (mm/kasan/report.c:595)
   __ipv6_chk_addr_and_flags (... net/ipv6/addrconf.c:1998)
   ipv6_chk_addr (net/ipv6/addrconf.c:2031 net/ipv6/addrconf.c:1972)
   rds_tcp_laddr_check (net/rds/tcp.c:370)
   rds_bind (net/rds/bind.c:248)
   __sys_bind (net/socket.c:1920)
   __x64_sys_bind (net/socket.c:1956)
   do_syscall_64 (arch/x86/entry/syscall_64.c:63)
   entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:121)

## References
- https://git.kernel.org/stable/c/76dd48886eeeb5fcf2b837d2f4c3d17eebeac9ef
- https://git.kernel.org/stable/c/78f75d632f74b8de0f081a128588f7c37d0d1164
- https://git.kernel.org/stable/c/8398bc477d3cb3e2b018a5aaac2bec0f69acda30
- https://git.kernel.org/stable/c/b1d480fce05f857dc438080cd8c9244b84a83494
- https://git.kernel.org/stable/c/ba95bce5dfe6e2ef602a87e0557225f2934ccb5c
- https://git.kernel.org/stable/c/c4933624a6f416ecfcc31ab58d585da1207a0597
- https://git.kernel.org/stable/c/f0d1fb05d70c8a561cd8d0473bcacafa2fc137ff
- https://git.kernel.org/stable/c/f8a8977af2134a1d91e5f9773cb7d9d53278c830
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74563.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74563
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
