# [H] drm/panel/panel-sitronix-st7701: Remove panel on DSI attach failure

## Summary
Severity: High
Advisory: CVE-2022-50750
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50750
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panel/panel-sitronix-st7701: Remove panel on DSI attach failure

In case mipi_dsi_attach() fails, call drm_panel_remove() to
avoid memory leak.

## References
- https://git.kernel.org/stable/c/0b7c47b7f358f932159a9d5beec9616ef8a0c6b4
- https://git.kernel.org/stable/c/13fc167e1645c43c631d7752d98e377f0e4cbb15
- https://git.kernel.org/stable/c/23fddf78eac8d79c56f93ab69b6c47a0816967c9
- https://git.kernel.org/stable/c/465611e812587e72bf235034edce0e51be3d6809
- https://git.kernel.org/stable/c/576828e59a0e03bbc763872912b04f3e3a1b3311
- https://git.kernel.org/stable/c/c62102165dd79284d42383d2f7ed17301bd8e629
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50750.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50750
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
