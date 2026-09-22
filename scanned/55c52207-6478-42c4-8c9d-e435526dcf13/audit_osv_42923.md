# [H] ocfs2: fix UBSAN array-index-out-of-bounds in ocfs2_sum_rightmost_rec

## Summary
Severity: High
Advisory: CVE-2026-72162
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72162
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: fix UBSAN array-index-out-of-bounds in ocfs2_sum_rightmost_rec

[BUG]
On-disk corruption setting l_next_free_rec to 0 in an inode's embedded
extent list triggers a UBSAN panic on the next write to that file.

[CAUSE]
ocfs2_sum_rightmost_rec() computes
i = le16_to_cpu(el->l_next_free_rec) - 1
and accesses el->l_recs[i] without validating i. When l_next_free_rec
is 0, i becomes -1; when l_next_free_rec exceeds l_count, i falls
past the end of the array. Either case violates the
__counted_by_le(l_count) annotation on l_recs[] and triggers UBSAN.

[FIX]
Validate the inode's embedded extent list when the inode is read, in
ocfs2_validate_inode_block(): l_count must be non-zero and no larger
than the inode block can hold, and l_next_free_rec must not exceed
l_count. A corrupt list is rejected at read time, before the b-tree
code can index l_recs[] out of bounds.

## References
- https://git.kernel.org/stable/c/452a8467be8143747292218212671deeb186d2ae
- https://git.kernel.org/stable/c/671889c553ea55e2da6a4f3b15f4c0fa40f2f0d1
- https://git.kernel.org/stable/c/858aa4965ffa8c0d4bb5dd835ac4f1c9a1dcab85
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72162.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72162
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
