# [M] drm/amdgpu: install stub fence into potential unused fence pointers

## Summary
Severity: Medium
Advisory: CVE-2023-53248
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53248
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.1.47, >=6.2.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: install stub fence into potential unused fence pointers

When using cpu to update page tables, vm update fences are unused.
Install stub fence into these fence pointers instead of NULL
to avoid NULL dereference when calling dma_fence_wait() on them.

## References
- https://git.kernel.org/stable/c/187916e6ed9d0c3b3abc27429f7a5f8c936bd1f0
- https://git.kernel.org/stable/c/78b25110eb8c6990f7f5096bc0136c12a2b4cc99
- https://git.kernel.org/stable/c/aa9e9ba5748c524eb0925a2ef6984b78793646d6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53248.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53248
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
