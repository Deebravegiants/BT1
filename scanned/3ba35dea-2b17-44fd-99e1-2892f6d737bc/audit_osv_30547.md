# [H] sctp: fix possible UAF in sctp_v6_available()

## Summary
Severity: High
Advisory: CVE-2024-53139
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53139
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: fix possible UAF in sctp_v6_available()

A lockdep report [1] with CONFIG_PROVE_RCU_LIST=y hints
that sctp_v6_available() is calling dev_get_by_index_rcu()
and ipv6_chk_addr() without holding rcu.

[1]
 =============================
 WARNING: suspicious RCU usage
 6.12.0-rc5-virtme #1216 Tainted: G        W
 -----------------------------
 net/core/dev.c:876 RCU-list traversed in non-reader section!!

other info that might help us debug this:

rcu_scheduler_active = 2, debug_locks = 1
 1 lock held by sctp_hello/31495:
 #0: ffff9f1ebbdb7418 (sk_lock-AF_INET6){+.+.}-{0:0}, at: sctp_bind (./arch/x86/include/asm/jump_label.h:27 net/sctp/socket.c:315) sctp

stack backtrace:
 CPU: 7 UID: 0 PID: 31495 Comm: sctp_hello Tainted: G        W          6.12.0-rc5-virtme #1216
 Tainted: [W]=WARN
 Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
 Call Trace:
  <TASK>
 dump_stack_lvl (lib/dump_stack.c:123)
 lockdep_rcu_suspicious (kernel/locking/lockdep.c:6822)
 dev_get_by_index_rcu (net/core/dev.c:876 (discriminator 7))
 sctp_v6_available (net/sctp/ipv6.c:701) sctp
 sctp_do_bind (net/sctp/socket.c:400 (discriminator 1)) sctp
 sctp_bind (net/sctp/socket.c:320) sctp
 inet6_bind_sk (net/ipv6/af_inet6.c:465)
 ? security_socket_bind (security/security.c:4581 (discriminator 1))
 __sys_bind (net/socket.c:1848 net/socket.c:1869)
 ? do_user_addr_fault (./include/linux/rcupdate.h:347 ./include/linux/rcupdate.h:880 ./include/linux/mm.h:729 arch/x86/mm/fault.c:1340)
 ? do_user_addr_fault (./arch/x86/include/asm/preempt.h:84 (discriminator 13) ./include/linux/rcupdate.h:98 (discriminator 13) ./include/linux/rcupdate.h:882 (discriminator 13) ./include/linux/mm.h:729 (discriminator 13) arch/x86/mm/fault.c:1340 (discriminator 13))
 __x64_sys_bind (net/socket.c:1877 (discriminator 1) net/socket.c:1875 (discriminator 1) net/socket.c:1875 (discriminator 1))
 do_syscall_64 (arch/x86/entry/common.c:52 (discriminator 1) arch/x86/entry/common.c:83 (discriminator 1))
 entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:130)
 RIP: 0033:0x7f59b934a1e7
 Code: 44 00 00 48 8b 15 39 8c 0c 00 f7 d8 64 89 02 b8 ff ff ff ff eb bd 66 2e 0f 1f 84 00 00 00 00 00 0f 1f 00 b8 31 00 00 00 0f 05 <48> 3d 01 f0 ff ff 73 01 c3 48 8b 0d 09 8c 0c 00 f7 d8 64 89 01 48
All code
========
   0:	44 00 00             	add    %r8b,(%rax)
   3:	48 8b 15 39 8c 0c 00 	mov    0xc8c39(%rip),%rdx        # 0xc8c43
   a:	f7 d8                	neg    %eax
   c:	64 89 02             	mov    %eax,%fs:(%rdx)
   f:	b8 ff ff ff ff       	mov    $0xffffffff,%eax
  14:	eb bd                	jmp    0xffffffffffffffd3
  16:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  1d:	00 00 00
  20:	0f 1f 00             	nopl   (%rax)
  23:	b8 31 00 00 00       	mov    $0x31,%eax
  28:	0f 05                	syscall
  2a:*	48 3d 01 f0 ff ff    	cmp    $0xfffffffffffff001,%rax		<-- trapping instruction
  30:	73 01                	jae    0x33
  32:	c3                   	ret
  33:	48 8b 0d 09 8c 0c 00 	mov    0xc8c09(%rip),%rcx        # 0xc8c43
  3a:	f7 d8                	neg    %eax
  3c:	64 89 01             	mov    %eax,%fs:(%rcx)
  3f:	48                   	rex.W

Code starting with the faulting instruction
===========================================
   0:	48 3d 01 f0 ff ff    	cmp    $0xfffffffffffff001,%rax
   6:	73 01                	jae    0x9
   8:	c3                   	ret
   9:	48 8b 0d 09 8c 0c 00 	mov    0xc8c09(%rip),%rcx        # 0xc8c19
  10:	f7 d8                	neg    %eax
  12:	64 89 01             	mov    %eax,%fs:(%rcx)
  15:	48                   	rex.W
 RSP: 002b:00007ffe2d0ad398 EFLAGS: 00000202 ORIG_RAX: 0000000000000031
 RAX: ffffffffffffffda RBX: 00007ffe2d0ad3d0 RCX: 00007f59b934a1e7
 RDX: 000000000000001c RSI: 00007ffe2d0ad3d0 RDI: 0000000000000005
 RBP: 0000000000000005 R08: 1999999999999999 R09: 0000000000000000
 R10: 00007f59b9253298 R11: 000000000000
---truncated---

## References
- https://git.kernel.org/stable/c/05656a66592759242c74063616291b7274d11b2f
- https://git.kernel.org/stable/c/ad975697211f4f2c4ce61c3ba524fd14d88ceab8
- https://git.kernel.org/stable/c/eb72e7fcc83987d5d5595b43222f23b295d5de7f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53139.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53139
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
