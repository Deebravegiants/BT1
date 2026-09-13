# [M] mptcp: init: protect sched with rcu_read_lock

## Summary
Severity: Medium
Advisory: CVE-2024-53047
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53047
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: init: protect sched with rcu_read_lock

Enabling CONFIG_PROVE_RCU_LIST with its dependence CONFIG_RCU_EXPERT
creates this splat when an MPTCP socket is created:

  =============================
  WARNING: suspicious RCU usage
  6.12.0-rc2+ #11 Not tainted
  -----------------------------
  net/mptcp/sched.c:44 RCU-list traversed in non-reader section!!

  other info that might help us debug this:

  rcu_scheduler_active = 2, debug_locks = 1
  no locks held by mptcp_connect/176.

  stack backtrace:
  CPU: 0 UID: 0 PID: 176 Comm: mptcp_connect Not tainted 6.12.0-rc2+ #11
  Hardware name: Bochs Bochs, BIOS Bochs 01/01/2011
  Call Trace:
   <TASK>
   dump_stack_lvl (lib/dump_stack.c:123)
   lockdep_rcu_suspicious (kernel/locking/lockdep.c:6822)
   mptcp_sched_find (net/mptcp/sched.c:44 (discriminator 7))
   mptcp_init_sock (net/mptcp/protocol.c:2867 (discriminator 1))
   ? sock_init_data_uid (arch/x86/include/asm/atomic.h:28)
   inet_create.part.0.constprop.0 (net/ipv4/af_inet.c:386)
   ? __sock_create (include/linux/rcupdate.h:347 (discriminator 1))
   __sock_create (net/socket.c:1576)
   __sys_socket (net/socket.c:1671)
   ? __pfx___sys_socket (net/socket.c:1712)
   ? do_user_addr_fault (arch/x86/mm/fault.c:1419 (discriminator 1))
   __x64_sys_socket (net/socket.c:1728)
   do_syscall_64 (arch/x86/entry/common.c:52 (discriminator 1))
   entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:130)

That's because when the socket is initialised, rcu_read_lock() is not
used despite the explicit comment written above the declaration of
mptcp_sched_find() in sched.c. Adding the missing lock/unlock avoids the
warning.

## References
- https://git.kernel.org/stable/c/3deb12c788c385e17142ce6ec50f769852fcec65
- https://git.kernel.org/stable/c/494eb22f9a7bd03783e60595a57611c209175f1a
- https://git.kernel.org/stable/c/cb8b81ad3e893a6d18dcdd3754cc2ea2a42c0136
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53047.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53047
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
