# [H] memcg: use round-robin victim selection in refill_stock

## Summary
Severity: High
Advisory: CVE-2026-53162
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53162
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

memcg: use round-robin victim selection in refill_stock

Harry Yoo reported that get_random_u32_below() is not safe to call in the
nmi context and memcg charge draining can happen in nmi context.

More specifically get_random_u32_below() is neither reentrant- nor
NMI-safe: it acquires a per-cpu local_lock via local_lock_irqsave() on the
batched_entropy_u32 state.  An NMI that lands on a CPU mid-update of the
ChaCha batch state and recurses into the random subsystem would corrupt
that state.  The memcg_stock local_trylock prevents re-entry on the percpu
stock itself, but cannot protect an unrelated subsystem's per-cpu lock.

Replace the random pick with a per-cpu round-robin counter stored in
memcg_stock_pcp and serialized by the same local_trylock that already
guards cached[] and nr_pages[].  No atomics, no random calls, no extra
locks needed.

## References
- https://git.kernel.org/stable/c/00731bd7e18f182a32ca54d6b176eaa470b51ed7
- https://git.kernel.org/stable/c/89bd8215e25aa6999cc51696da418e0d422bc5e0
- https://git.kernel.org/stable/c/c0cafe24d3f6534294c4b2bc2d47734ff7cbd313
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53162.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53162
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
