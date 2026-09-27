# [H] drm/xe: Wait on external BO kernel fences in exec IOCTL

## Summary
Severity: High
Advisory: CVE-2026-74440
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74440
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Wait on external BO kernel fences in exec IOCTL

Before arming a user job, xe_exec_ioctl() only added the VM's
dma-resv KERNEL slot as a dependency. That slot covers rebinds and
the kernel operations of the VM's private BOs, but not external BOs
(bo->vm == NULL), which carry their kernel operations (evictions,
moves, ...) in their own dma-resv KERNEL slot.

The DMA_RESV_USAGE_KERNEL slot is the cross-driver contract for
memory management operations that must complete before the BO or its
backing store may be used: any accessor is required to wait on the
KERNEL fences before touching the resv. By skipping the external BOs'
KERNEL slots, the exec path violated that contract and could schedule
a user job while a kernel operation on an external BO mapped by the VM
was still in flight, racing against it and potentially reading or
writing memory that was being moved.

Replace the VM-only dependency with an iteration over every object
locked by the exec, adding each object's KERNEL slot as a job
dependency. This covers the VM resv (rebinds and private BOs) as well
as every external BO, mirroring the drm_gpuvm_resv_add_fence() call
that later publishes the job fence to the same set of objects.
Long-running mode continues to skip this, as before.

(cherry picked from commit a6b842acf3ddd1efc53a56de9260cfa718fb35e7)

## References
- https://git.kernel.org/stable/c/1738db550334adca0e7fcf0ef684198fb7462779
- https://git.kernel.org/stable/c/21976fe5258494ac38b63d103be81bf1180ae4ae
- https://git.kernel.org/stable/c/5d363d00bc9799b90a0dc89eb1c5dcb909c042ee
- https://git.kernel.org/stable/c/af80e2bfde9312c76b60cf9274248dce0410b30d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74440.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74440
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
