# [M] drm/i915: Fix a memory leak with reused mmap_offset

## Summary
Severity: Medium
Advisory: CVE-2023-53002
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53002
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915: Fix a memory leak with reused mmap_offset

drm_vma_node_allow() and drm_vma_node_revoke() should be called in
balanced pairs. We call drm_vma_node_allow() once per-file everytime a
user calls mmap_offset, but only call drm_vma_node_revoke once per-file
on each mmap_offset. As the mmap_offset is reused by the client, the
per-file vm_count may remain non-zero and the rbtree leaked.

Call drm_vma_node_allow_once() instead to prevent that memory leak.

## References
- https://git.kernel.org/stable/c/0220e4fe178c3390eb0291cdb34912d66972db8a
- https://git.kernel.org/stable/c/0bdc4b4ba7206c452ee81c82fa66e39d0e1780fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53002.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53002
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
