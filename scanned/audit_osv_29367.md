# [H] drm/amd/display: Check pipe offset before setting vblank

## Summary
Severity: High
Advisory: CVE-2024-42120
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42120
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.98, >=6.2.0 <6.6.39, >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Check pipe offset before setting vblank

pipe_ctx has a size of MAX_PIPES so checking its index before accessing
the array.

This fixes an OVERRUN issue reported by Coverity.

## References
- https://git.kernel.org/stable/c/0b3702f9d43d163fd05e43b7d7e22e766dbef329
- https://git.kernel.org/stable/c/5396a70e8cf462ec5ccf2dc8de103c79de9489e6
- https://git.kernel.org/stable/c/96bf81cc1bd058bb8af6e755a548e926e934dfd1
- https://git.kernel.org/stable/c/b2e9abc95583ac7bbb2c47da4d476a798146dfd6
- https://git.kernel.org/stable/c/c5ec2afeeee4c91cebc4eff6d4f1ecf4047259f4
- https://git.kernel.org/stable/c/d2c3645a4a5ae5d933b4116c305d9d82b8199dbf
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42120.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42120
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
