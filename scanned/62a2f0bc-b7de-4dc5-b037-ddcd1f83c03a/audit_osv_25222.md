# [M] CVE-2023-3220

## Summary
Severity: Medium
Advisory: CVE-2023-3220
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-20
Source: https://osv.dev/vulnerability/CVE-2023-3220
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.1-rc8. dpu_crtc_atomic_check in drivers/gpu/drm/msm/disp/dpu1/dpu_crtc.c lacks check of the return value of kzalloc() and will cause the NULL Pointer Dereference.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=93340e10b9c5fc86730d149636e0aa8b47bb5a34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3220.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3220
