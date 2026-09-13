# [H] drm/vmwgfx: fix guest_memory_dirty bitfield clobbered as size

## Summary
Severity: High
Advisory: CVE-2026-80702
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80702
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: fix guest_memory_dirty bitfield clobbered as size

Two sites in vmwgfx_resource.c assign boolean literals to
res->guest_memory_size, which is an unsigned long allocation-size
field; the intended target is the adjacent res->guest_memory_dirty
bitfield.  After the assignments the field holds 0 or 1 instead of
the resource's MOB allocation size:

  - vmw_resource_release()       writes 0 (false), and
  - vmw_resource_unbind_list()   writes 1 (true).

Subsequent revalidation paths read guest_memory_size when computing
the dirty page range (vmw_bo_dirty_transfer_to_res()) and the buffer
allocation size (vmw_resource_buf_alloc()), producing zero-length
walks or wrap-around ranges that read or write past the MOB bitmap.
The dirty-tracking intent of the original code (mark the resource as
dirtied since the last sync) is also lost, since guest_memory_dirty
is never updated.

Rename both assignments to guest_memory_dirty.

## References
- https://git.kernel.org/stable/c/21bbe38faee4a195d33a93e3908e307807f7745d
- https://git.kernel.org/stable/c/282f261cb035e5f01a486f76d356b7e9dbfba73f
- https://git.kernel.org/stable/c/3b2bb16a5b622867140d69925db411ac8ecb3b2b
- https://git.kernel.org/stable/c/83195b778f2d109a3a4f3ffaba4dce7e4cdb58aa
- https://git.kernel.org/stable/c/9d6cbb76fe9cd760351f6b0b20f1bf788eab8fa6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80702.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80702
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
