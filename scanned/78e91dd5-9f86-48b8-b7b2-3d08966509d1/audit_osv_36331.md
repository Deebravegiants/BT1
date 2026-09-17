# [H] mm/vma: fix anon_vma UAF on mremap() faulted, unfaulted merge

## Summary
Severity: High
Advisory: CVE-2026-23077
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-23077
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/vma: fix anon_vma UAF on mremap() faulted, unfaulted merge

Patch series "mm/vma: fix anon_vma UAF on mremap() faulted, unfaulted
merge", v2.

Commit 879bca0a2c4f ("mm/vma: fix incorrectly disallowed anonymous VMA
merges") introduced the ability to merge previously unavailable VMA merge
scenarios.

However, it is handling merges incorrectly when it comes to mremap() of a
faulted VMA adjacent to an unfaulted VMA.  The issues arise in three
cases:

1. Previous VMA unfaulted:

              copied -----|
                          v
	|-----------|.............|
	| unfaulted |(faulted VMA)|
	|-----------|.............|
	     prev

2. Next VMA unfaulted:

              copied -----|
                          v
	            |.............|-----------|
	            |(faulted VMA)| unfaulted |
                    |.............|-----------|
		                      next

3. Both adjacent VMAs unfaulted:

              copied -----|
                          v
	|-----------|.............|-----------|
	| unfaulted |(faulted VMA)| unfaulted |
	|-----------|.............|-----------|
	     prev                      next

This series fixes each of these cases, and introduces self tests to assert
that the issues are corrected.

I also test a further case which was already handled, to assert that my
changes continues to correctly handle it:

4. prev unfaulted, next faulted:

              copied -----|
                          v
	|-----------|.............|-----------|
	| unfaulted |(faulted VMA)|  faulted  |
	|-----------|.............|-----------|
	     prev                      next

This bug was discovered via a syzbot report, linked to in the first patch
in the series, I confirmed that this series fixes the bug.

I also discovered that we are failing to check that the faulted VMA was
not forked when merging a copied VMA in cases 1-3 above, an issue this
series also addresses.

I also added self tests to assert that this is resolved (and confirmed
that the tests failed prior to this).

I also cleaned up vma_expand() as part of this work, renamed
vma_had_uncowed_parents() to vma_is_fork_child() as the previous name was
unduly confusing, and simplified the comments around this function.


This patch (of 4):

Commit 879bca0a2c4f ("mm/vma: fix incorrectly disallowed anonymous VMA
merges") introduced the ability to merge previously unavailable VMA merge
scenarios.

The key piece of logic introduced was the ability to merge a faulted VMA
immediately next to an unfaulted VMA, which relies upon dup_anon_vma() to
correctly handle anon_vma state.

In the case of the merge of an existing VMA (that is changing properties
of a VMA and then merging if those properties are shared by adjacent
VMAs), dup_anon_vma() is invoked correctly.

However in the case of the merge of a new VMA, a corner case peculiar to
mremap() was missed.

The issue is that vma_expand() only performs dup_anon_vma() if the target
(the VMA that will ultimately become the merged VMA): is not the next VMA,
i.e.  the one that appears after the range in which the new VMA is to be
established.

A key insight here is that in all other cases other than mremap(), a new
VMA merge either expands an existing VMA, meaning that the target VMA will
be that VMA, or would have anon_vma be NULL.

Specifically:

* __mmap_region() - no anon_vma in place, initial mapping.
* do_brk_flags() - expanding an existing VMA.
* vma_merge_extend() - expanding an existing VMA.
* relocate_vma_down() - no anon_vma in place, initial mapping.

In addition, we are in the unique situation of needing to duplicate
anon_vma state from a VMA that is neither the previous or next VMA being
merged with.

dup_anon_vma() deals exclusively with the target=unfaulted, src=faulted
case.  This leaves four possibilities, in each case where the copied VMA
is faulted:

1. Previous VMA unfaulted:

              copied -----|
                       
---truncated---

## References
- https://git.kernel.org/stable/c/61f67c230a5e7c741c352349ea80147fbe65bfae
- https://git.kernel.org/stable/c/a4d9dbfc1bab16e25fefd34b5e537a46bed8fc96
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23077.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23077
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
