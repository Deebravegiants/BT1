# [H] alpha: fix user-space corruption during memory compaction

## Summary
Severity: High
Advisory: CVE-2026-43258
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43258
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.16 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

alpha: fix user-space corruption during memory compaction

Alpha systems can suffer sporadic user-space crashes and heap
corruption when memory compaction is enabled.

Symptoms include SIGSEGV, glibc allocator failures (e.g. "unaligned
tcache chunk"), and compiler internal errors. The failures disappear
when compaction is disabled or when using global TLB invalidation.

The root cause is insufficient TLB shootdown during page migration.
Alpha relies on ASN-based MM context rollover for instruction cache
coherency, but this alone is not sufficient to prevent stale data or
instruction translations from surviving migration.

Fix this by introducing a migration-specific helper that combines:
  - MM context invalidation (ASN rollover),
  - immediate per-CPU TLB invalidation (TBI),
  - synchronous cross-CPU shootdown when required.

The helper is used only by migration/compaction paths to avoid changing
global TLB semantics.

Additionally, update flush_tlb_other(), pte_clear(), to use
READ_ONCE()/WRITE_ONCE() for correct SMP memory ordering.

This fixes observed crashes on both UP and SMP Alpha systems.

## References
- https://git.kernel.org/stable/c/03e42b5f7ad4c2c3db8bd384bab7990d5d53c90f
- https://git.kernel.org/stable/c/bab8d762a8dbb816b10011e13b87d1bca91e5f77
- https://git.kernel.org/stable/c/d4ca6ca2c6f5a1d19d9014c5b36d96637846b5d6
- https://git.kernel.org/stable/c/dd5712f3379cfe760267cdd28ff957d9ab4e51c7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43258.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43258
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
