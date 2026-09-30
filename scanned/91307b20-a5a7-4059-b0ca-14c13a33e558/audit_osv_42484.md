# [H] drm/imagination: acquire vm_ctx->lock before mapping memory to GPU VM

## Summary
Severity: High
Advisory: CVE-2026-68260
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68260
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/imagination: acquire vm_ctx->lock before mapping memory to GPU VM

The drm gpuvm code doesn't protect find operation against map operation,
and the driver needs to ensure a map operation shouldn't happen when a
find operation is in progress.

In some cases a find operation will be in progress when doing map/unmap
operations, and the find operation will do a NULL pointer dereference.

An example of the stack trace of such NULL dereference is shown below:

```
Unable to handle kernel access to user memory without uaccess routines at
virtual address 0000000000000010

[<ffffffff01e989d4>] drm_gpuva_find+0x28/0x6c [drm_gpuvm]
[<ffffffff01ed3a40>] pvr_vm_unmap+0x34/0x68 [powervr]
[<ffffffff01ec69da>] pvr_ioctl_vm_unmap+0x2e/0x50 [powervr]
[<ffffffff8080ce0a>] drm_ioctl_kernel+0x8e/0xdc
[<ffffffff8080d016>] drm_ioctl+0x1be/0x3e0
[<ffffffff802bec3e>] __riscv_sys_ioctl+0xba/0xc4
[<ffffffff80d858b2>] do_trap_ecall_u+0x23e/0x3f4
[<ffffffff80d92288>] handle_exception+0x168/0x174
```

As all occurences of drm_gpuva_find*() are already guarded by
vm_ctx->lock, make pvr_vm_map() to acquire this lock to prevent
disturbing any find operation. This fixes the NULL deference problem in
drm_gpuva_find*().

## References
- https://git.kernel.org/stable/c/15f58d44c24477a6ebffa44ec05207b81cfa55d9
- https://git.kernel.org/stable/c/17e2030f37600994440f875dc410615d5c66ee6d
- https://git.kernel.org/stable/c/1f1f2618e44b21a7d4eb30d3bbd7e015ffbbbadf
- https://git.kernel.org/stable/c/6253bb56bb2ebdf317d8b599ce737a2510cc2e17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68260.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68260
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
