# [H] drm/amdgpu/mes: fix use-after-free issue

## Summary
Severity: High
Advisory: CVE-2024-38581
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38581
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu/mes: fix use-after-free issue

Delete fence fallback timer to fix the ramdom
use-after-free issue.

v2: move to amdgpu_mes.c

## References
- https://git.kernel.org/stable/c/0f98c144c15c8fc0f3176c994bd4e727ef718a5c
- https://git.kernel.org/stable/c/39cfce75168c11421d70b8c0c65f6133edccb82a
- https://git.kernel.org/stable/c/70b1bf6d9edc8692d241f59a65f073aec6d501de
- https://git.kernel.org/stable/c/948255282074d9367e01908b3f5dcf8c10fc9c3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38581.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38581
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
