# [H] powerpc/spufs: fix out-of-bounds access in spufs_mem_mmap_access()

## Summary
Severity: High
Advisory: CVE-2026-68474
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68474
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/spufs: fix out-of-bounds access in spufs_mem_mmap_access()

spufs_mem_mmap_access() computes the local store offset as
address - vma->vm_start, but bounds-checks it against vma->vm_end
instead of the local store size. On 64-bit, offset is always well
below vma->vm_end, so the clamp never fires and len stays unbounded
against the LS_SIZE buffer returned by ctx->ops->get_ls().

Reject offsets at or beyond LS_SIZE and clamp len to the remaining
space, mirroring the guard already used by spufs_mem_mmap_fault() and
spufs_ps_fault().

## References
- https://git.kernel.org/stable/c/3c1e92f75e11a11492b8cb901fceeb9f16ae6415
- https://git.kernel.org/stable/c/47b87f469a35b5ffc81c16eee6b13a9b6c8d55c6
- https://git.kernel.org/stable/c/4efa313b15925bdd864784865d6585174979294b
- https://git.kernel.org/stable/c/913feef74354c653f10ecd4631df7618a95c49c2
- https://git.kernel.org/stable/c/9d3569bfdceda69d5ffd5148901e57b69954d9ef
- https://git.kernel.org/stable/c/aa7aa8ba40c089762d821e3987aaae19e1f5705c
- https://git.kernel.org/stable/c/d479a7711f8ff127946467b910d947bd971b94ed
- https://git.kernel.org/stable/c/d97a8f3668949a8a9d1f6202f8c53446f2d89aa7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68474.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68474
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
