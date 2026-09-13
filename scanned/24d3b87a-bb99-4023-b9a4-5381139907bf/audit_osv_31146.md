# [H] bpf: bpf_local_storage: Always use bpf_mem_alloc in PREEMPT_RT

## Summary
Severity: High
Advisory: CVE-2024-58070
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58070
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: bpf_local_storage: Always use bpf_mem_alloc in PREEMPT_RT

In PREEMPT_RT, kmalloc(GFP_ATOMIC) is still not safe in non preemptible
context. bpf_mem_alloc must be used in PREEMPT_RT. This patch is
to enforce bpf_mem_alloc in the bpf_local_storage when CONFIG_PREEMPT_RT
is enabled.

[   35.118559] BUG: sleeping function called from invalid context at kernel/locking/spinlock_rt.c:48
[   35.118566] in_atomic(): 1, irqs_disabled(): 0, non_block: 0, pid: 1832, name: test_progs
[   35.118569] preempt_count: 1, expected: 0
[   35.118571] RCU nest depth: 1, expected: 1
[   35.118577] INFO: lockdep is turned off.
    ...
[   35.118647]  __might_resched+0x433/0x5b0
[   35.118677]  rt_spin_lock+0xc3/0x290
[   35.118700]  ___slab_alloc+0x72/0xc40
[   35.118723]  __kmalloc_noprof+0x13f/0x4e0
[   35.118732]  bpf_map_kzalloc+0xe5/0x220
[   35.118740]  bpf_selem_alloc+0x1d2/0x7b0
[   35.118755]  bpf_local_storage_update+0x2fa/0x8b0
[   35.118784]  bpf_sk_storage_get_tracing+0x15a/0x1d0
[   35.118791]  bpf_prog_9a118d86fca78ebb_trace_inet_sock_set_state+0x44/0x66
[   35.118795]  bpf_trace_run3+0x222/0x400
[   35.118820]  __bpf_trace_inet_sock_set_state+0x11/0x20
[   35.118824]  trace_inet_sock_set_state+0x112/0x130
[   35.118830]  inet_sk_state_store+0x41/0x90
[   35.118836]  tcp_set_state+0x3b3/0x640

There is no need to adjust the gfp_flags passing to the
bpf_mem_cache_alloc_flags() which only honors the GFP_KERNEL.
The verifier has ensured GFP_KERNEL is passed only in sleepable context.

It has been an old issue since the first introduction of the
bpf_local_storage ~5 years ago, so this patch targets the bpf-next.

bpf_mem_alloc is needed to solve it, so the Fixes tag is set
to the commit when bpf_mem_alloc was first used in the bpf_local_storage.

## References
- https://git.kernel.org/stable/c/3392fa605d7c5708c5fbe02e4fbdac547c3b7352
- https://git.kernel.org/stable/c/8eef6ac4d70eb1f0099fff93321d90ce8fa49ee1
- https://git.kernel.org/stable/c/b0027500000dfcb8ee952557d565064cea22c43e
- https://git.kernel.org/stable/c/c1d398a3af7e59d7fef351c84fed7ebb575d1f1a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58070.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58070
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
