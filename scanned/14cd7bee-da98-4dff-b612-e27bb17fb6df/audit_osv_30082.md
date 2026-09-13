# [H] drm/amdkfd: amdkfd_free_gtt_mem clear the correct pointer

## Summary
Severity: High
Advisory: CVE-2024-49991
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49991
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <6.1.118, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: amdkfd_free_gtt_mem clear the correct pointer

Pass pointer reference to amdgpu_bo_unref to clear the correct pointer,
otherwise amdgpu_bo_unref clear the local variable, the original pointer
not set to NULL, this could cause use-after-free bug.

## References
- https://git.kernel.org/stable/c/30ceb873cc2e97348d9da2265b2d1ddf07f682e1
- https://git.kernel.org/stable/c/6c9289806591807e4e3be9a23df8ee2069180055
- https://git.kernel.org/stable/c/71f3240f82987f0f070ea5bed559033de7d4c0e1
- https://git.kernel.org/stable/c/c86ad39140bbcb9dc75a10046c2221f657e8083b
- https://git.kernel.org/stable/c/e7831613cbbcd9058d3658fbcdc5d5884ceb2e0c
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49991.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49991
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
