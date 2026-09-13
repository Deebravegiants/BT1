# [H] irq_work: Fix use-after-free in irq_work_single() on PREEMPT_RT

## Summary
Severity: High
Advisory: CVE-2026-64073
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64073
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

irq_work: Fix use-after-free in irq_work_single() on PREEMPT_RT

On PREEMPT_RT, non-HARD irq_work runs in per-CPU kthreads via
run_irq_workd(), so irq_work_sync() uses rcuwait() to wait for BUSY==0.

After irq_work_single() clears BUSY via atomic_cmpxchg(), it still
dereferences @work for irq_work_is_hard() and rcuwait_wake_up().

An irq_work_sync() caller on another CPU that enters after BUSY is cleared
can observe BUSY==0 immediately, return, and free the work before those
accesses complete — causing a use-after-free.

Fix this by wrapping run_irq_workd() in guard(rcu)() so that the entire
irq_work_single() execution is within an RCU read-side critical
section. Then add synchronize_rcu() in irq_work_sync() after
rcuwait_wait_event() to ensure the caller waits for the RCU grace period
before returning, preventing premature frees.

## References
- https://git.kernel.org/stable/c/18c0456ea2615b1a743a6db739c74411c3b42bc6
- https://git.kernel.org/stable/c/2dc79362302922cb18f35e262712b5e58de65442
- https://git.kernel.org/stable/c/684a78183c54c23e70d1cba320f7fc184604210b
- https://git.kernel.org/stable/c/81b582784518196eff1050212a046bc29d3a05dd
- https://git.kernel.org/stable/c/91840be8f710370607f949a627e070896faeddb8
- https://git.kernel.org/stable/c/eef4f71b46a9929ac33e968538c9dd5d96a02460
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64073.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64073
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
