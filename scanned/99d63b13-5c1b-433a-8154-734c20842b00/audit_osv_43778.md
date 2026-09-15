# [H] accel/amxdna: Fix page-insertion errors in amdxdna_insert_pages()

## Summary
Severity: High
Advisory: CVE-2026-74721
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74721
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amxdna: Fix page-insertion errors in amdxdna_insert_pages()

Two error paths in amdxdna_insert_pages() called vma->vm_ops->close(vma)
before returning an error code to the caller.  This is incorrect:
amdxdna_gem_obj_mmap() registers an HMM interval notifier before calling
amdxdna_insert_pages(), and on a hard error it jumps to hmm_unreg to undo
that registration.  Calling vm_ops->close() manually — which drops the
shmem pages_pin_count and the GEM object reference that backs the VMA —
before the mmap syscall has even returned causes those resources to be
released while the VMA is still alive.  The kernel VMA teardown will call
vm_ops->close() a second time when the process later unmaps the range,
producing a reference count underflow.

Replace both hard-error returns with a deferred-fault approach that keeps
the VMA alive and retries page insertion through the HMM range-fault path.

## References
- https://git.kernel.org/stable/c/1501e4d07c6fee0d50531a0d1cb2be01a63e6e75
- https://git.kernel.org/stable/c/8d51e0fd3e698919d2adeff71936377f0c0d4aa0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74721.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74721
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
