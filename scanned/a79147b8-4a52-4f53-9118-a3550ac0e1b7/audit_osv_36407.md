# [H] futex: Fix UaF between futex_key_to_node_opt() and vma_replace_policy()

## Summary
Severity: High
Advisory: CVE-2026-23415
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-23415
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

futex: Fix UaF between futex_key_to_node_opt() and vma_replace_policy()

During futex_key_to_node_opt() execution, vma->vm_policy is read under
speculative mmap lock and RCU. Concurrently, mbind() may call
vma_replace_policy() which frees the old mempolicy immediately via
kmem_cache_free().

This creates a race where __futex_key_to_node() dereferences a freed
mempolicy pointer, causing a use-after-free read of mpol->mode.

[  151.412631] BUG: KASAN: slab-use-after-free in __futex_key_to_node (kernel/futex/core.c:349)
[  151.414046] Read of size 2 at addr ffff888001c49634 by task e/87

[  151.415969] Call Trace:

[  151.416732]  __asan_load2 (mm/kasan/generic.c:271)
[  151.416777]  __futex_key_to_node (kernel/futex/core.c:349)
[  151.416822]  get_futex_key (kernel/futex/core.c:374 kernel/futex/core.c:386 kernel/futex/core.c:593)

Fix by adding rcu to __mpol_put().

## References
- https://git.kernel.org/stable/c/190a8c48ff623c3d67cb295b4536a660db2012aa
- https://git.kernel.org/stable/c/7e196194ea27bd49adf3551e2aceb83498eb73fe
- https://git.kernel.org/stable/c/853f70c67d1b37e368fdcb3e328c4b8c04f53ac0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23415.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23415
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
