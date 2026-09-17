# [H] arm64: tlb: Flush walk cache when unsharing PMD tables

## Summary
Severity: High
Advisory: CVE-2026-63875
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63875
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: tlb: Flush walk cache when unsharing PMD tables

When huge_pmd_unshare() is called to unshare a PMD table, the
tlb_unshare_pmd_ptdesc() function sets tlb->unshared_tables=true
but the aarch64 tlb_flush() only checked tlb->freed_tables to
determine whether to use TLBF_NONE (vae1is, invalidates walk
cache) or TLBF_NOWALKCACHE (vale1is, leaf-only).

This caused the stale PMD page table entry to remain in the walk cache
after unshare, potentially leading to incorrect page table walks.

Fix by including unshared_tables in the check, so that when
unsharing tables, TLBF_NONE is used and the walk cache is properly
invalidated.

Here is the detailed distinction between vae1is and vale1is:

| Instruction Combination  | Actual Invalidation Scope                         |
| ------------------------ | --------------------------------------------------|
| `VAE1IS`  + TTL=`0`      | All entries at all levels (full invalidation)     |
| `VAE1IS`  + TTL=`2` (L2) | Non-leaf at Level 0/1 + leaf at Level 2           |
| `VALE1IS` + TTL=`0`      | Leaf entries at all levels (non-leaf not cleared) |
| `VALE1IS` + TTL=`2` (L2) | Leaf entry at Level 2 only                        |

## References
- https://git.kernel.org/stable/c/0199c9d57861f17b556b6cba1f765c7cce79745b
- https://git.kernel.org/stable/c/47490bbb05c8c0e09cc3cfd237d8934ffc340583
- https://git.kernel.org/stable/c/48125cd9c55cbe297b59fd1f9bda48b0960bd181
- https://git.kernel.org/stable/c/8ca7284da0e67b3e71d90ec17f08286774245ad9
- https://git.kernel.org/stable/c/c2ff4764e03e7a8d758352f4aceb8fe1be6ac971
- https://git.kernel.org/stable/c/d766a49d9b55705c4737cd8bb5d3faa2d31330fd
- https://git.kernel.org/stable/c/dced308d7d6a0de1c09d2058f38f1aaaf5cbb914
- https://git.kernel.org/stable/c/fe93e907b1af03cc229a80aa64a570a103d2b279
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63875.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63875
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
