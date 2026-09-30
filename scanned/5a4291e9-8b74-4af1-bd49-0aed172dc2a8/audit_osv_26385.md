# [H] drm/amdkfd: Add sync after creating vram bo

## Summary
Severity: High
Advisory: CVE-2023-53009
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53009
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Add sync after creating vram bo

There will be data corruption on vram allocated by svm
if the initialization is not complete and application is
writting on the memory. Adding sync to wait for the
initialization completion is to resolve this issue.

## References
- https://git.kernel.org/stable/c/92af2d3b57a1afdfdcafb1c6a07ffd89cf3e98fb
- https://git.kernel.org/stable/c/ba029e9991d9be90a28b6a0ceb25e9a6fb348829
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53009.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53009
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
