# [H] net: rose: fix timer races against user threads

## Summary
Severity: High
Advisory: CVE-2025-21718
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21718
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: rose: fix timer races against user threads

Rose timers only acquire the socket spinlock, without
checking if the socket is owned by one user thread.

Add a check and rearm the timers if needed.

BUG: KASAN: slab-use-after-free in rose_timer_expiry+0x31d/0x360 net/rose/rose_timer.c:174
Read of size 2 at addr ffff88802f09b82a by task swapper/0/0

CPU: 0 UID: 0 PID: 0 Comm: swapper/0 Not tainted 6.13.0-rc5-syzkaller-00172-gd1bf27c4e176 #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 09/13/2024
Call Trace:
 <IRQ>
  __dump_stack lib/dump_stack.c:94 [inline]
  dump_stack_lvl+0x241/0x360 lib/dump_stack.c:120
  print_address_description mm/kasan/report.c:378 [inline]
  print_report+0x169/0x550 mm/kasan/report.c:489
  kasan_report+0x143/0x180 mm/kasan/report.c:602
  rose_timer_expiry+0x31d/0x360 net/rose/rose_timer.c:174
  call_timer_fn+0x187/0x650 kernel/time/timer.c:1793
  expire_timers kernel/time/timer.c:1844 [inline]
  __run_timers kernel/time/timer.c:2418 [inline]
  __run_timer_base+0x66a/0x8e0 kernel/time/timer.c:2430
  run_timer_base kernel/time/timer.c:2439 [inline]
  run_timer_softirq+0xb7/0x170 kernel/time/timer.c:2449
  handle_softirqs+0x2d4/0x9b0 kernel/softirq.c:561
  __do_softirq kernel/softirq.c:595 [inline]
  invoke_softirq kernel/softirq.c:435 [inline]
  __irq_exit_rcu+0xf7/0x220 kernel/softirq.c:662
  irq_exit_rcu+0x9/0x30 kernel/softirq.c:678
  instr_sysvec_apic_timer_interrupt arch/x86/kernel/apic/apic.c:1049 [inline]
  sysvec_apic_timer_interrupt+0xa6/0xc0 arch/x86/kernel/apic/apic.c:1049
 </IRQ>

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0d5bca3be27bfcf8f980f2fed49b6cbb7dafe4a1
- https://git.kernel.org/stable/c/1409b45d4690308c502c6caf22f01c3c205b4717
- https://git.kernel.org/stable/c/1992fb261c90e9827cf5dc3115d89bb0853252c9
- https://git.kernel.org/stable/c/51c128ba038cf1b79d605cbee325919b45ab95a5
- https://git.kernel.org/stable/c/52f5aff33ca73b2c2fa93f40a3de308012e63cf4
- https://git.kernel.org/stable/c/58051a284ac18a3bb815aac6289a679903ddcc3f
- https://git.kernel.org/stable/c/5de7665e0a0746b5ad7943554b34db8f8614a196
- https://git.kernel.org/stable/c/f55c88e3ca5939a6a8a329024aed8f3d98eea8e4
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21718.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21718
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
