# [H] mm/huge_memory: fix huge_zero_pfn race

## Summary
Severity: High
Advisory: CVE-2026-74632
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74632
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.267, >=5.11.0 <5.15.218, >=5.13.0 <6.1.184, >=5.16.0 <6.6.153, >=6.2.0 <6.12.104, >=6.7.0 <6.18.45, >=6.13.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/huge_memory: fix huge_zero_pfn race

Patch series "mm/huge_memory: fix huge_zero_pfn race", v2.

There is a subtle race in the reference-counted huge_zero_folio
implementation.

The fast path atomic logic fails to account for the fact that the shrinker
(which drops the final huge_zero_refcount pin) can overwrite huge_zero_pfn
with the ~0UL sentinel value in shrink_huge_zero_folio_scan() after a
racing get_huge_zero_folio() installed a valid value there.

This results in huge_zero_folio being correctly set but huge_zero_pfn
being set incorrectly and thus is_huge_zero_pfn() and consequently
is_huge_zero_pmd() will misidentify the huge zero folio as being an
ordinary THP folio.

This can result in the huge zero folio being split and otherwise treated
incorrectly.

The solution to this is very subtle as there is an atomic fast path, and
thus ordering in weakly ordered architectures has to be treated very
carefully.

The first commit fixes the issue by introducing a spinlock around
huge_zero_[pfn, folio, refcount] write, with careful consideration paid to
load/store ordering in the fast path.  It is placed first and kept as
small as possible so that it can be backported on its own.

The second commit is a pure cleanup which reworks the
CONFIG_PERSISTENT_HUGE_ZERO_FOLIO logic to better separate the persistent
logic from the dynamically allocated one.


This patch (of 2):

If !CONFIG_PERSISTENT_HUGE_ZERO_FOLIO, the huge_zero_folio is refcounted
by huge_zero_refcount and returned by mm_get_huge_zero_folio().

When the caller is done with the huge zero page, its reference count is
decremented.  Only a shrinker can set the reference count to zero.

A race can unfortunately occur between a shrinker decrementing the
reference count to zero and a concurrent page fault.

This is because shrink_huge_zero_folio_scan() might, if very unlucky, be
preempted between setting huge_zero_refcount to zero and writing an
invalid value.

During this time get_huge_zero_folio() could write to huge_zero_pfn before
shrink_huge_zero_folio_scan() resumes.

In this event the huge zero folio will be persistently misidentified
causing the THP code path to be entered inappropriately for the huge zero
folio:

                CPU 0                                   CPU 1
=======================================|=================================
shrink_huge_zero_folio_scan()          |
   atomic_cmpxchg() sets refcount to 0 |
   xchg() sets huge_zero_folio to NULL | get_huge_zero_folio()
                 |                     |    atomic_inc_not_zero() -> zero
      preempted for a long time        |    Allocate new huge zero folio
                 |                     |    Write valid huge_zero_folio
                 v                     |    Write valid huge_zero_pfn
  Overwrite huge_zero_pfn with ~0UL   <--- Invalid overwrite!

This results in is_huge_zero_pfn() and is_huge_zero_pmd() incorrectly
returning false for a huge zero page which could result in issues like the
huge zero folio being incorrectly split.

Note that the issue is with huge_zero_pfn not huge_zero_folio, as
get_huge_zero_folio() uses cmpxchg() gated on huge_zero_folio being NULL
with a retry loop and shrink_huge_zero_folio_scan() uses xchg() to set
huge_zero_folio.

Fix the issue by introducing a spinlock, huge_zero_lock, to prevent
concurrent write of huge_zero_folio, huge_zero_pfn and huge_zero_refcount.

There needs to be significant care taken here to ensure correctness:

The fast path in get_huge_zero_folio() uses atomic_inc_not_zero(), which
is outside of the critical section, and means huge zero allocation is
gated on zero huge_zero_refcount.

The fast path doesn't use huge_zero_lock, so the critical section is
irrelevant to it.

So invariants are required - huge_zero_refcount MUST:

* Only be set in the huge_zero_lock critical section to ensure
  serialisation of huge_zero_pfn, huge_zero_folio and
---truncated---

## References
- https://git.kernel.org/stable/c/105d04edbec83010df5728f74d17fd9c108e7553
- https://git.kernel.org/stable/c/33192a26cddea7a7e4ca66e5c3eebd36fa8be2bb
- https://git.kernel.org/stable/c/6024f6d0d9b9ca5138bfc4ac6f6e4bdf616e42b3
- https://git.kernel.org/stable/c/9332b080ad57650d1dc582e54517f9fc78ef89cc
- https://git.kernel.org/stable/c/9c0fd1802ce06d7709f0bae4edeb085288f28764
- https://git.kernel.org/stable/c/ab7e4b407c7f58d1a003134eff3841f303d5ccc2
- https://git.kernel.org/stable/c/b7041ba61c5da4e0b56f9be58cfb87d7689724e4
- https://git.kernel.org/stable/c/f3a874a903053c53fb53ba287ea9eacda69c68e8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74632.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74632
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
