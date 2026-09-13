# [H] mm/vma: do not try to unmap a VMA if mmap_prepare() invoked from mmap()

## Summary
Severity: High
Advisory: CVE-2026-53373
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53373
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/vma: do not try to unmap a VMA if mmap_prepare() invoked from mmap()

The mmap_prepare hook functionality includes the ability to invoke
mmap_prepare() from the mmap() hook of existing 'stacked' drivers, that is
ones which are capable of calling the mmap hooks of other drivers/file
systems (e.g.  overlayfs, shm).

As part of the mmap_prepare action functionality, we deal with errors by
unmapping the VMA should one arise.  This works in the usual mmap_prepare
case, as we invoke this action at the last moment, when the VMA is
established in the maple tree.

However, the mmap() hook passes a not-fully-established VMA pointer to the
caller (which is the motivation behind the mmap_prepare() work), which is
detached.

So attempting to unmap a VMA in this state will be problematic, with the
most obvious symptom being a warning in vma_mark_detached(), because the
VMA is already detached.

It's also unncessary - the mmap() handler will clean up the VMA on error.

So to fix this issue, this patch propagates whether or not an mmap action
is being completed via the compatibility layer or directly.

If the former, then we do not attempt VMA cleanup, if the latter, then we
do.

This patch also updates the userland VMA tests to reflect the change.

## References
- https://git.kernel.org/stable/c/5394bcb746503f2ae4b206212416dccea78e3773
- https://git.kernel.org/stable/c/619eab23e1ce7c97e54bfc5a417306d94b3f6f13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53373.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53373
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
