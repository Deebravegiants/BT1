# [H] bpf: Clear rb node linkage when freeing bpf_rb_root

## Summary
Severity: High
Advisory: CVE-2026-74344
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74344
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Clear rb node linkage when freeing bpf_rb_root

bpf_rb_root_free() detaches the root by copying the current rb_root_cached
and then replacing the live root with RB_ROOT_CACHED. It then walks the
copied root and drops each object contained in the tree.

This leaves the rb node state intact while dropping the object. If the
object is refcounted and survives the drop, its bpf_rb_node_kern still
contains an owner pointer to the freed root and stale rb tree linkage. If
a later bpf_rb_root allocation reuses the same address, bpf_rbtree_remove()
can incorrectly pass the owner check and call rb_erase_cached() on a node
whose rb pointers belong to the old tree.

Mirror the list draining behavior by marking nodes as busy while the root
is being detached, then clear the rb node and release the owner before
dropping the containing object. This makes surviving nodes unowned and
safe to reject from remove or accept for a later add.

## References
- https://git.kernel.org/stable/c/2eb39de4962f842d653e96818ae372665cd481fd
- https://git.kernel.org/stable/c/4a7910ee060d8ce55612f5b3cc267f3a265a3cec
- https://git.kernel.org/stable/c/574612793bed416f6c05fe7c9b50e9eb0441997e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74344.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74344
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
