# [H] vhost/vdpa: validate virtqueue index in mmap and fault paths

## Summary
Severity: High
Advisory: CVE-2026-74312
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74312
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost/vdpa: validate virtqueue index in mmap and fault paths

vhost_vdpa_mmap() and vhost_vdpa_fault() use vma->vm_pgoff as a
virtqueue index for get_vq_notification(), but they do not validate
that the index is smaller than v->nvqs.

The ioctl path already performs both a bounds check and
array_index_nospec(), but the mmap/fault path only checks that the
index fits in u16. This allows an out-of-range queue index to reach
driver-specific get_vq_notification() callbacks.

Fix this by extracting a unified vhost_vdpa_get_vq_notification()
helper that validates the queue index against v->nvqs and applies
array_index_nospec() before calling the driver callback. Both the
mmap and fault paths use this helper, and the bounds checking is
consolidated into a single location.

From source inspection, the most defensible impact is out-of-bounds
access in the callback path, potentially leading to invalid PFN
remaps and crash/DoS.

## References
- https://git.kernel.org/stable/c/0f310bac6db9bd3bb1655707d692d9d2a86eeb17
- https://git.kernel.org/stable/c/1f5f94c6c6b2e4eaa5b45815509e21d0c6cfa81e
- https://git.kernel.org/stable/c/2b3f79b90b231a682315fe2191bb71925650e183
- https://git.kernel.org/stable/c/32ac9097aa2463fcfc12f61cc4a9ebc3579cba7d
- https://git.kernel.org/stable/c/4bf5a51963ff816f7443702dc536b9327cf5e550
- https://git.kernel.org/stable/c/55a644031e610ea93fbde2702c7b8f267476552f
- https://git.kernel.org/stable/c/929e4f044621c8cc30b612fb74e1410bef09e41b
- https://git.kernel.org/stable/c/bbba4f92515238d76018e9b75e41b16d83df52c8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74312.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74312
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
