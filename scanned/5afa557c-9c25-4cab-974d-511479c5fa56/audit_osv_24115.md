# [H] android: binder: stop saving a pointer to the VMA

## Summary
Severity: High
Advisory: CVE-2022-50240
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50240
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

android: binder: stop saving a pointer to the VMA

Do not record a pointer to a VMA outside of the mmap_lock for later use. 
This is unsafe and there are a number of failure paths *after* the
recorded VMA pointer may be freed during setup.  There is no callback to
the driver to clear the saved pointer from generic mm code.  Furthermore,
the VMA pointer may become stale if any number of VMA operations end up
freeing the VMA so saving it was fragile to being with.

Instead, change the binder_alloc struct to record the start address of the
VMA and use vma_lookup() to get the vma when needed.  Add lockdep
mmap_lock checks on updates to the vma pointer to ensure the lock is held
and depend on that lock for synchronization of readers and writers - which
was already the case anyways, so the smp_wmb()/smp_rmb() was not
necessary.

[akpm@linux-foundation.org: fix drivers/android/binder_alloc_selftest.c]

## References
- https://git.kernel.org/stable/c/015ac18be7de25d17d6e5f1643cb3b60bfbe859e
- https://git.kernel.org/stable/c/1ec3f76a436d750fd5023caec5da0494fc2870d2
- https://git.kernel.org/stable/c/27a594bc7a7c8238d239e3cdbcf2edfa3bbe9a1b
- https://git.kernel.org/stable/c/622ef885a89ad04cfb76ee478fb44f051125d1f1
- https://git.kernel.org/stable/c/925e6b6f82c9c80ab3c17acbde8d16f349da7d26
- https://git.kernel.org/stable/c/a43cfc87caaf46710c8027a8c23b8a55f1078f19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50240.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50240
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
