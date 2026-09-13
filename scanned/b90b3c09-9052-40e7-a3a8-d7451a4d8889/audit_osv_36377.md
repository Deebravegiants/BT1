# [H] netfilter: nf_tables: unconditionally bump set->nelems before insertion

## Summary
Severity: High
Advisory: CVE-2026-23272
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-23272
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <6.1.177, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: unconditionally bump set->nelems before insertion

In case that the set is full, a new element gets published then removed
without waiting for the RCU grace period, while RCU reader can be
walking over it already.

To address this issue, add the element transaction even if set is full,
but toggle the set_full flag to report -ENFILE so the abort path safely
unwinds the set to its previous state.

As for element updates, decrement set->nelems to restore it.

A simpler fix is to call synchronize_rcu() in the error path.
However, with a large batch adding elements to already maxed-out set,
this could cause noticeable slowdown of such batches.

## References
- https://git.kernel.org/stable/c/25fcaef7948912652905e96922f36583a84fffed
- https://git.kernel.org/stable/c/6826131c7674329335ca25df2550163eb8a1fd0c
- https://git.kernel.org/stable/c/86bc4b1a0f672d47ac19f9022432cb6a2e01cb33
- https://git.kernel.org/stable/c/ccb8c8f3c1127cf34d18c737309897c68046bf21
- https://git.kernel.org/stable/c/def602e498a4f951da95c95b1b8ce8ae68aa733a
- https://git.kernel.org/stable/c/e3ccb11fc8249759d23326038c8db987ddaabc77
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23272.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23272
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
