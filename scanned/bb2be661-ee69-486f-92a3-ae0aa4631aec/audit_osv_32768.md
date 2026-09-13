# [H] mm, slab: clean up slab->obj_exts always

## Summary
Severity: High
Advisory: CVE-2025-37908
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37908
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm, slab: clean up slab->obj_exts always

When memory allocation profiling is disabled at runtime or due to an
error, shutdown_mem_profiling() is called: slab->obj_exts which
previously allocated remains.
It won't be cleared by unaccount_slab() because of
mem_alloc_profiling_enabled() not true. It's incorrect, slab->obj_exts
should always be cleaned up in unaccount_slab() to avoid following error:

[...]BUG: Bad page state in process...
..
[...]page dumped because: page still charged to cgroup

[andriy.shevchenko@linux.intel.com: fold need_slab_obj_ext() into its only user]

## References
- https://git.kernel.org/stable/c/01db0e1a48345aa1937f3bdfc7c7108d03ebcf7e
- https://git.kernel.org/stable/c/be8250786ca94952a19ce87f98ad9906448bc9ef
- https://git.kernel.org/stable/c/dab2a13059a475b6392550f882276e170fe2fcff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37908.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37908
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
