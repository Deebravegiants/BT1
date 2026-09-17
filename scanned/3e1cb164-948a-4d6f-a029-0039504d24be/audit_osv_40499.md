# [H] drm/amdgpu: zero-initialize GART table on allocation

## Summary
Severity: High
Advisory: CVE-2026-53374
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53374
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: zero-initialize GART table on allocation

GART TLB is flushed after unmapping but not after mapping. Since
amdgpu_bo_create_kernel() does not zero-initialize the buffer, when a
single PTE is written the TLB may speculatively load other uninitialized
entries from the same cacheline. Those garbage entries can appear valid,
and a subsequent write to another PTE in the same cacheline may cause the
GPU to use a stale garbage PTE from the TLB.

Fix this by calling memset_io() to zero-initialize the GART table with
gart_pte_flags immediately after allocation.

Using AMDGPU_GEM_CREATE_VRAM_CLEARED, SDMA-based clear will not work
since SDMA needs GART to be initialized to work.

(cherry picked from commit d9af8263b82b6eaa60c5718e0c6631c5037e4b24)

## References
- https://git.kernel.org/stable/c/40df11255d71b02e20e70579f1b12b687e396e26
- https://git.kernel.org/stable/c/791941be5da125d9a1b228582bfdc300c05d05b3
- https://git.kernel.org/stable/c/8ae8b9e74bab94aab1d79f1688129bcc61c8b29a
- https://git.kernel.org/stable/c/91fbb5e635c8fb1b49e15c19da06480089ef719f
- https://git.kernel.org/stable/c/b17175d0a375b3ed5e81597dac4983fdb46e478d
- https://git.kernel.org/stable/c/e6c2e6c2e1fa066968a16aca1cb66cd1bdde7741
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53374.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53374
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
