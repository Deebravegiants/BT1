# [H] rxrpc: Fix irq-disabled in local_bh_enable()

## Summary
Severity: High
Advisory: CVE-2025-38525
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38525
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix irq-disabled in local_bh_enable()

The rxrpc_assess_MTU_size() function calls down into the IP layer to find
out the MTU size for a route.  When accepting an incoming call, this is
called from rxrpc_new_incoming_call() which holds interrupts disabled
across the code that calls down to it.  Unfortunately, the IP layer uses
local_bh_enable() which, config dependent, throws a warning if IRQs are
enabled:

WARNING: CPU: 1 PID: 5544 at kernel/softirq.c:387 __local_bh_enable_ip+0x43/0xd0
...
RIP: 0010:__local_bh_enable_ip+0x43/0xd0
...
Call Trace:
 <TASK>
 rt_cache_route+0x7e/0xa0
 rt_set_nexthop.isra.0+0x3b3/0x3f0
 __mkroute_output+0x43a/0x460
 ip_route_output_key_hash+0xf7/0x140
 ip_route_output_flow+0x1b/0x90
 rxrpc_assess_MTU_size.isra.0+0x2a0/0x590
 rxrpc_new_incoming_peer+0x46/0x120
 rxrpc_alloc_incoming_call+0x1b1/0x400
 rxrpc_new_incoming_call+0x1da/0x5e0
 rxrpc_input_packet+0x827/0x900
 rxrpc_io_thread+0x403/0xb60
 kthread+0x2f7/0x310
 ret_from_fork+0x2a/0x230
 ret_from_fork_asm+0x1a/0x30
...
hardirqs last  enabled at (23): _raw_spin_unlock_irq+0x24/0x50
hardirqs last disabled at (24): _raw_read_lock_irq+0x17/0x70
softirqs last  enabled at (0): copy_process+0xc61/0x2730
softirqs last disabled at (25): rt_add_uncached_list+0x3c/0x90

Fix this by moving the call to rxrpc_assess_MTU_size() out of
rxrpc_init_peer() and further up the stack where it can be done without
interrupts disabled.

It shouldn't be a problem for rxrpc_new_incoming_call() to do it after the
locks are dropped as pmtud is going to be performed by the I/O thread - and
we're in the I/O thread at this point.

## References
- https://git.kernel.org/stable/c/2029f21f10dedb88c0f86abffcf8d6c21dcf6040
- https://git.kernel.org/stable/c/8ac0b3baa7d8f732bd9e5cbf1d8b57e4802c6b36
- https://git.kernel.org/stable/c/d94b82d452ca27a200cd67660dc48476386651d8
- https://git.kernel.org/stable/c/e4d2878369d590bf8455e3678a644e503172eafa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38525.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38525
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
