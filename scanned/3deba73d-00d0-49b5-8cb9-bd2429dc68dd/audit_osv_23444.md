# [H] mm: don't try to NUMA-migrate COW pages that have other uses

## Summary
Severity: High
Advisory: CVE-2022-48797
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48797
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.102, >=5.11.0 <5.15.25, >=5.16.0 <5.16.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: don't try to NUMA-migrate COW pages that have other uses

Oded Gabbay reports that enabling NUMA balancing causes corruption with
his Gaudi accelerator test load:

 "All the details are in the bug, but the bottom line is that somehow,
  this patch causes corruption when the numa balancing feature is
  enabled AND we don't use process affinity AND we use GUP to pin pages
  so our accelerator can DMA to/from system memory.

  Either disabling numa balancing, using process affinity to bind to
  specific numa-node or reverting this patch causes the bug to
  disappear"

and Oded bisected the issue to commit 09854ba94c6a ("mm: do_wp_page()
simplification").

Now, the NUMA balancing shouldn't actually be changing the writability
of a page, and as such shouldn't matter for COW.  But it appears it
does.  Suspicious.

However, regardless of that, the condition for enabling NUMA faults in
change_pte_range() is nonsensical.  It uses "page_mapcount(page)" to
decide if a COW page should be NUMA-protected or not, and that makes
absolutely no sense.

The number of mappings a page has is irrelevant: not only does GUP get a
reference to a page as in Oded's case, but the other mappings migth be
paged out and the only reference to them would be in the page count.

Since we should never try to NUMA-balance a page that we can't move
anyway due to other references, just fix the code to use 'page_count()'.
Oded confirms that that fixes his issue.

Now, this does imply that something in NUMA balancing ends up changing
page protections (other than the obvious one of making the page
inaccessible to get the NUMA faulting information).  Otherwise the COW
simplification wouldn't matter - since doing the GUP on the page would
make sure it's writable.

The cause of that permission change would be good to figure out too,
since it clearly results in spurious COW events - but fixing the
nonsensical test that just happened to work before is obviously the
CorrectThing(tm) to do regardless.

## References
- https://git.kernel.org/stable/c/254090925e16abd914c87b4ad1b489440d89c4c3
- https://git.kernel.org/stable/c/80d47f5de5e311cbc0d01ebb6ee684e8f4c196c6
- https://git.kernel.org/stable/c/b3dc4b9d3ca68b370c4aeab5355007eedf948849
- https://git.kernel.org/stable/c/d187eeb02d18446e5e54ed6bcbf8b47e6551daea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48797.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48797
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
