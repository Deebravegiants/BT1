# [H] drm/amdkfd: Fix a race condition of vram buffer unref in svm code

## Summary
Severity: High
Advisory: CVE-2023-52825
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52825
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Fix a race condition of vram buffer unref in svm code

prange->svm_bo unref can happen in both mmu callback and a callback after
migrate to system ram. Both are async call in different tasks. Sync svm_bo
unref operation to avoid random "use-after-free".

## References
- https://git.kernel.org/stable/c/50f35a907c4f9ed431fd3dbb8b871ef1cbb0718e
- https://git.kernel.org/stable/c/709c348261618da7ed89d6c303e2ceb9e453ba74
- https://git.kernel.org/stable/c/7d43cdd22cd81a2b079e864c4321b9aba4c6af34
- https://git.kernel.org/stable/c/c772eacbd6d0845fc922af8716bb9d29ae27b8cf
- https://git.kernel.org/stable/c/fc0210720127cc6302e6d6f3de48f49c3fcf5659
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52825.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52825
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
