# [M] drm/xe: Drop VM dma-resv lock on xe_sync_in_fence_get failure in exec IOCTL

## Summary
Severity: Medium
Advisory: CVE-2024-53086
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53086
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Drop VM dma-resv lock on xe_sync_in_fence_get failure in exec IOCTL

Upon failure all locks need to be dropped before returning to the user.

(cherry picked from commit 7d1a4258e602ffdce529f56686925034c1b3b095)

## References
- https://git.kernel.org/stable/c/64a2b6ed4bfd890a0e91955dd8ef8422a3944ed9
- https://git.kernel.org/stable/c/96397b1e25dda8389dea63ec914038a170bf953d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53086.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53086
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
