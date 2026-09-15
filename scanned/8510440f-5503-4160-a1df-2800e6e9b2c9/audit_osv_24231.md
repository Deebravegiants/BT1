# [H] drm/amdkfd: Fix memory leakage

## Summary
Severity: High
Advisory: CVE-2022-50528
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2022-50528
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Fix memory leakage

This patch fixes potential memory leakage and seg fault
in  _gpuvm_import_dmabuf() function

## References
- https://git.kernel.org/stable/c/7356d8e367d0e025a568e369c4cf575722cac60f
- https://git.kernel.org/stable/c/75818afff631e1ea785a82c3e8bb82eb0dee539c
- https://git.kernel.org/stable/c/8876793e56ec69b3be2a883b4bc440df3dbb1865
- https://git.kernel.org/stable/c/c65564790048fa416ccd26a8945c7ec0cf9ef0b7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50528.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50528
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
