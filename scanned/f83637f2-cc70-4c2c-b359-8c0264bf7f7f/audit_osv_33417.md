# [H] bpf: Sync pending IRQ work before freeing ring buffer

## Summary
Severity: High
Advisory: CVE-2025-40319
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40319
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Sync pending IRQ work before freeing ring buffer

Fix a race where irq_work can be queued in bpf_ringbuf_commit()
but the ring buffer is freed before the work executes.
In the syzbot reproducer, a BPF program attached to sched_switch
triggers bpf_ringbuf_commit(), queuing an irq_work. If the ring buffer
is freed before this work executes, the irq_work thread may accesses
freed memory.
Calling `irq_work_sync(&rb->work)` ensures that all pending irq_work
complete before freeing the buffer.

## References
- https://git.kernel.org/stable/c/10ca3b2eec384628bc9f5d8190aed9427ad2dde6
- https://git.kernel.org/stable/c/430e15544f11f8de26b2b5109c7152f71b78295e
- https://git.kernel.org/stable/c/47626748a2a00068dbbd5836d19076637b4e235b
- https://git.kernel.org/stable/c/4e9077638301816a7d73fa1e1b4c1db4a7e3b59c
- https://git.kernel.org/stable/c/6451141103547f4efd774e912418a3b4318046c6
- https://git.kernel.org/stable/c/de2ce6b14bc3e565708a39bdba3ef9162aeffc72
- https://git.kernel.org/stable/c/e1828c7a8d8135e21ff6adaaa9458c32aae13b11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40319.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40319
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
