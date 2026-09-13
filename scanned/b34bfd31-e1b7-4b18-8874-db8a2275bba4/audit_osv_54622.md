# [M] CVE-2024-22386

## Summary
Severity: Medium
Advisory: CVE-2024-22386
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2024-22386
Type: osv

## Details
A race condition was found in the Linux kernel's drm/exynos device driver in exynos_drm_crtc_atomic_disable() function. This can result in a null pointer dereference issue, possibly leading to a kernel panic or denial of service issue.

## References
- https://bugzilla.openanolis.cn/show_bug.cgi?id=8147
