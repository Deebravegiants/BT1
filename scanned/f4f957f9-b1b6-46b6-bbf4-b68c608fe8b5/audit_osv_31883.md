# [H] mm: abort vma_modify() on merge out of memory failure

## Summary
Severity: High
Advisory: CVE-2025-21932
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21932
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: abort vma_modify() on merge out of memory failure

The remainder of vma_modify() relies upon the vmg state remaining pristine
after a merge attempt.

Usually this is the case, however in the one edge case scenario of a merge
attempt failing not due to the specified range being unmergeable, but
rather due to an out of memory error arising when attempting to commit the
merge, this assumption becomes untrue.

This results in vmg->start, end being modified, and thus the proceeding
attempts to split the VMA will be done with invalid start/end values.

Thankfully, it is likely practically impossible for us to hit this in
reality, as it would require a maple tree node pre-allocation failure that
would likely never happen due to it being 'too small to fail', i.e.  the
kernel would simply keep retrying reclaim until it succeeded.

However, this scenario remains theoretically possible, and what we are
doing here is wrong so we must correct it.

The safest option is, when this scenario occurs, to simply give up the
operation.  If we cannot allocate memory to merge, then we cannot allocate
memory to split either (perhaps moreso!).

Any scenario where this would be happening would be under very extreme
(likely fatal) memory pressure, so it's best we give up early.

So there is no doubt it is appropriate to simply bail out in this
scenario.

However, in general we must if at all possible never assume VMG state is
stable after a merge attempt, since merge operations update VMG fields. 
As a result, additionally also make this clear by storing start, end in
local variables.

The issue was reported originally by syzkaller, and by Brad Spengler (via
an off-list discussion), and in both instances it manifested as a
triggering of the assert:

	VM_WARN_ON_VMG(start >= end, vmg);

In vma_merge_existing_range().

It seems at least one scenario in which this is occurring is one in which
the merge being attempted is due to an madvise() across multiple VMAs
which looks like this:

        start     end
          |<------>|
     |----------|------|
     |   vma    | next |
     |----------|------|

When madvise_walk_vmas() is invoked, we first find vma in the above
(determining prev to be equal to vma as we are offset into vma), and then
enter the loop.

We determine the end of vma that forms part of the range we are
madvise()'ing by setting 'tmp' to this value:

		/* Here vma->vm_start <= start < (end|vma->vm_end) */
		tmp = vma->vm_end;

We then invoke the madvise() operation via visit(), letting prev get
updated to point to vma as part of the operation:

		/* Here vma->vm_start <= start < tmp <= (end|vma->vm_end). */
		error = visit(vma, &prev, start, tmp, arg);

Where the visit() function pointer in this instance is
madvise_vma_behavior().

As observed in syzkaller reports, it is ultimately madvise_update_vma()
that is invoked, calling vma_modify_flags_name() and vma_modify() in turn.

Then, in vma_modify(), we attempt the merge:

	merged = vma_merge_existing_range(vmg);
	if (merged)
		return merged;

We invoke this with vmg->start, end set to start, tmp as such:

        start  tmp
          |<--->|
     |----------|------|
     |   vma    | next |
     |----------|------|

We find ourselves in the merge right scenario, but the one in which we
cannot remove the middle (we are offset into vma).

Here we have a special case where vmg->start, end get set to perhaps
unintuitive values - we intended to shrink the middle VMA and expand the
next.

This means vmg->start, end are set to...  vma->vm_start, start.

Now the commit_merge() fails, and vmg->start, end are left like this. 
This means we return to the rest of vma_modify() with vmg->start, end
(here denoted as start', end') set as:

  start' end'
     |<-->|
     |----------|------|
     |   vma    | next |
     |----------|------|

So we now erroneously try to split accordingly.  This is where the
unfortunate
---truncated---

## References
- https://git.kernel.org/stable/c/47b16d0462a460000b8f05dfb1292377ac48f3ca
- https://git.kernel.org/stable/c/53fd215f7886a1e8dea5a9ca1391dbb697fff601
- https://git.kernel.org/stable/c/79636d2981b066acd945117387a9533f56411f6f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21932.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21932
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
