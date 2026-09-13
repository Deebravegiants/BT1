# [H] drm/amd/display: Use krealloc_array() in dal_vector_reserve()

## Summary
Severity: High
Advisory: CVE-2026-53329
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-53329
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.260, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Use krealloc_array() in dal_vector_reserve()

[Why & How]
dal_vector_reserve() computes the allocation size as
"capacity * vector->struct_size" using uint32_t arithmetic, which can
silently wrap to a small value on overflow. This would cause krealloc to
return a smaller buffer than expected, leading to heap overflows on
subsequent vector appends.

Replace krealloc() with krealloc_array() which performs an internal
overflow check and returns NULL on wrap, preventing the issue.

(cherry picked from commit 37668568641ccc4cc1dbca4923d0a16609dd5707)

## References
- https://git.kernel.org/stable/c/201151e120f0062bcda21cad5d007b82725ad23b
- https://git.kernel.org/stable/c/31180638a33acad12c863132704a76536fb66211
- https://git.kernel.org/stable/c/9540b0a4d13e4ede64ae1197d66a176d2149daa9
- https://git.kernel.org/stable/c/a914aa802669e073f014dae2e5708633b5cecd34
- https://git.kernel.org/stable/c/b15825deac1acff72638bbc8f05b89ceef8dfb13
- https://git.kernel.org/stable/c/da48bc4461b8a5ebfb9264c9b191a701d8e99009
- https://git.kernel.org/stable/c/de988c7a31f0774f07894cfe4802996f318e2870
- https://git.kernel.org/stable/c/e09689286385a66311ac6922af95339d7a3cef8d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53329.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53329
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
