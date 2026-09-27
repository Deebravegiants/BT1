# [H] KVM: x86: Use __try_cmpxchg_user() to update guest PTE A/D bits

## Summary
Severity: High
Advisory: CVE-2022-49562
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49562
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.17.13, >=5.18.0 <5.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: Use __try_cmpxchg_user() to update guest PTE A/D bits

Use the recently introduced __try_cmpxchg_user() to update guest PTE A/D
bits instead of mapping the PTE into kernel address space.  The VM_PFNMAP
path is broken as it assumes that vm_pgoff is the base pfn of the mapped
VMA range, which is conceptually wrong as vm_pgoff is the offset relative
to the file and has nothing to do with the pfn.  The horrific hack worked
for the original use case (backing guest memory with /dev/mem), but leads
to accessing "random" pfns for pretty much any other VM_PFNMAP case.

## References
- https://git.kernel.org/stable/c/38b888911e8dc89b89d8147cfb1d2dbe6373bf78
- https://git.kernel.org/stable/c/8089e5e1d18402fb8152d6b6815450a36fffa9b0
- https://git.kernel.org/stable/c/f122dfe4476890d60b8c679128cd2259ec96a24c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49562.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49562
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
