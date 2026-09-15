# [H] ocfs2: fix out-of-bounds write in ocfs2_remove_refcount_extent

## Summary
Severity: High
Advisory: CVE-2026-80638
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80638
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: fix out-of-bounds write in ocfs2_remove_refcount_extent

[BUG]
Unlinking a refcounted file whose refcount tree has leaf blocks
triggers a fortify panic due to an out-of-bounds write.

[CAUSE]
When the last leaf block is removed from a refcount tree,
ocfs2_remove_refcount_extent() converts the root back to leaf mode
with a bulk memset on &rb->rf_records. rf_records sits in an anonymous
union with rf_list. rf_list.l_tree_depth aliases rf_records.rl_count,
and is 0 for a single-level tree. With rl_count equal to 0, the memset
writes past the 16-byte declared size of rf_records, which the fortify
checker catches.

[FIX]
Replace the bulk memset on &rb->rf_records with a correctly-bounded
memset on rl_recs[] alone, after setting rl_count to the correct value.

## References
- https://git.kernel.org/stable/c/1ec3cca2d8b6b9ff6584ca626d4c8918bbf48d44
- https://git.kernel.org/stable/c/f5255516ec7add3a6d5d37853ad5a9a9ddb14305
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80638.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80638
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
