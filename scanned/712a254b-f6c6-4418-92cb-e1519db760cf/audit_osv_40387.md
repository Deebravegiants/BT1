# [H] bpf: fix mm lifecycle in open-coded task_vma iterator

## Summary
Severity: High
Advisory: CVE-2026-53085
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53085
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: fix mm lifecycle in open-coded task_vma iterator

The open-coded task_vma iterator reads task->mm locklessly and acquires
mmap_read_trylock() but never calls mmget(). If the task exits
concurrently, the mm_struct can be freed as it is not
SLAB_TYPESAFE_BY_RCU, resulting in a use-after-free.

Safely read task->mm with a trylock on alloc_lock and acquire an mm
reference. Drop the reference via bpf_iter_mmput_async() in _destroy()
and error paths. bpf_iter_mmput_async() is a local wrapper around
mmput_async() with a fallback to mmput() on !CONFIG_MMU.

Reject irqs-disabled contexts (including NMI) up front. Operations used
by _next() and _destroy() (mmap_read_unlock, bpf_iter_mmput_async)
take spinlocks with IRQs disabled (pool->lock, pi_lock). Running from
NMI or from a tracepoint that fires with those locks held could
deadlock.

A trylock on alloc_lock is used instead of the blocking task_lock()
(get_task_mm) to avoid a deadlock when a softirq BPF program iterates
a task that already holds its alloc_lock on the same CPU.

## References
- https://git.kernel.org/stable/c/239cec25a22662dbd80f57d94b38178c8be95269
- https://git.kernel.org/stable/c/43683bb280330f3d36f0f2a3932a4867b9603e9c
- https://git.kernel.org/stable/c/d0862de7c866c5bd7c32531f66738c21197af888
- https://git.kernel.org/stable/c/d8e27d2d22b6e2df3a0125b8c08e9aace38c954c
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53085.json
- https://access.redhat.com/security/cve/CVE-2026-53085
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53085.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53085
- https://bugzilla.redhat.com/show_bug.cgi?id=2492404
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
