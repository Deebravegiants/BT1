# [H] smc: Fix use-after-free in tcp_write_timer_handler().

## Summary
Severity: High
Advisory: CVE-2023-53781
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53781
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.2.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

smc: Fix use-after-free in tcp_write_timer_handler().

With Eric's ref tracker, syzbot finally found a repro for
use-after-free in tcp_write_timer_handler() by kernel TCP
sockets. [0]

If SMC creates a kernel socket in __smc_create(), the kernel
socket is supposed to be freed in smc_clcsock_release() by
calling sock_release() when we close() the parent SMC socket.

However, at the end of smc_clcsock_release(), the kernel
socket's sk_state might not be TCP_CLOSE.  This means that
we have not called inet_csk_destroy_sock() in __tcp_close()
and have not stopped the TCP timers.

The kernel socket's TCP timers can be fired later, so we
need to hold a refcnt for net as we do for MPTCP subflows
in mptcp_subflow_create_socket().

[0]:
leaked reference.
 sk_alloc (./include/net/net_namespace.h:335 net/core/sock.c:2108)
 inet_create (net/ipv4/af_inet.c:319 net/ipv4/af_inet.c:244)
 __sock_create (net/socket.c:1546)
 smc_create (net/smc/af_smc.c:3269 net/smc/af_smc.c:3284)
 __sock_create (net/socket.c:1546)
 __sys_socket (net/socket.c:1634 net/socket.c:1618 net/socket.c:1661)
 __x64_sys_socket (net/socket.c:1672)
 do_syscall_64 (arch/x86/entry/common.c:50 arch/x86/entry/common.c:80)
 entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:120)
==================================================================
BUG: KASAN: slab-use-after-free in tcp_write_timer_handler (net/ipv4/tcp_timer.c:378 net/ipv4/tcp_timer.c:624 net/ipv4/tcp_timer.c:594)
Read of size 1 at addr ffff888052b65e0d by task syzrepro/18091

CPU: 0 PID: 18091 Comm: syzrepro Tainted: G        W          6.3.0-rc4-01174-gb5d54eb5899a #7
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.0-1.amzn2022.0.1 04/01/2014
Call Trace:
 <IRQ>
 dump_stack_lvl (lib/dump_stack.c:107)
 print_report (mm/kasan/report.c:320 mm/kasan/report.c:430)
 kasan_report (mm/kasan/report.c:538)
 tcp_write_timer_handler (net/ipv4/tcp_timer.c:378 net/ipv4/tcp_timer.c:624 net/ipv4/tcp_timer.c:594)
 tcp_write_timer (./include/linux/spinlock.h:390 net/ipv4/tcp_timer.c:643)
 call_timer_fn (./arch/x86/include/asm/jump_label.h:27 ./include/linux/jump_label.h:207 ./include/trace/events/timer.h:127 kernel/time/timer.c:1701)
 __run_timers.part.0 (kernel/time/timer.c:1752 kernel/time/timer.c:2022)
 run_timer_softirq (kernel/time/timer.c:2037)
 __do_softirq (./arch/x86/include/asm/jump_label.h:27 ./include/linux/jump_label.h:207 ./include/trace/events/irq.h:142 kernel/softirq.c:572)
 __irq_exit_rcu (kernel/softirq.c:445 kernel/softirq.c:650)
 irq_exit_rcu (kernel/softirq.c:664)
 sysvec_apic_timer_interrupt (arch/x86/kernel/apic/apic.c:1107 (discriminator 14))
 </IRQ>

## References
- https://git.kernel.org/stable/c/1cc41c8acfc1ee30b4868559058db97fa44b0137
- https://git.kernel.org/stable/c/9744d2bf19762703704ecba885b7ac282c02eacf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53781.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53781
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
