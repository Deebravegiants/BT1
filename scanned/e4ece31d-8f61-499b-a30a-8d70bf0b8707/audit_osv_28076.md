# [H] drm/amdgpu: once more fix the call oder in amdgpu_ttm_move() v2

## Summary
Severity: High
Advisory: CVE-2024-27400
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-27400
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: once more fix the call oder in amdgpu_ttm_move() v2

This reverts drm/amdgpu: fix ftrace event amdgpu_bo_move always move
on same heap. The basic problem here is that after the move the old
location is simply not available any more.

Some fixes were suggested, but essentially we should call the move
notification before actually moving things because only this way we have
the correct order for DMA-buf and VM move notifications as well.

Also rework the statistic handling so that we don't update the eviction
counter before the move.

v2: add missing NULL check

## References
- https://git.kernel.org/stable/c/0c7ed3ed35eec9138b88d42217b5a6b9a62bda4d
- https://git.kernel.org/stable/c/5c25b169f9a0b34ee410891a96bc9d7b9ed6f9be
- https://git.kernel.org/stable/c/9a4f6e138720b6e9adf7b82a71d0292f3f276480
- https://git.kernel.org/stable/c/d3a9331a6591e9df64791e076f6591f440af51c3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DW2MIOIMOFUSNLHLRYX23AFR36BMKD65/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OTB4HWU2PTVW5NEYHHLOCXDKG3PYA534/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27400.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27400
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
