# [M] drm/amdgpu: fix memory leak in mes self test

## Summary
Severity: Medium
Advisory: CVE-2023-53370
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53370
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.1.47, >=6.2.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix memory leak in mes self test

The fences associated with mes queue have to be freed
up during amdgpu_ring_fini.

## References
- https://git.kernel.org/stable/c/31d7c3a4fc3d312a0646990767647925d5bde540
- https://git.kernel.org/stable/c/8d8c96efcec95736622381b2afc0fe9e317f88aa
- https://git.kernel.org/stable/c/ce3288d8d654b252ba832626e7de481c195ef20a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53370.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53370
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
