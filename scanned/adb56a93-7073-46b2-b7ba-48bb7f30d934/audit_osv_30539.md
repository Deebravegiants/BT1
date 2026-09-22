# [H] Revert "mmc: dw_mmc: Fix IDMAC operation with pages bigger than 4K"

## Summary
Severity: High
Advisory: CVE-2024-53127
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53127
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.119, >=6.2.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "mmc: dw_mmc: Fix IDMAC operation with pages bigger than 4K"

The commit 8396c793ffdf ("mmc: dw_mmc: Fix IDMAC operation with pages
bigger than 4K") increased the max_req_size, even for 4K pages, causing
various issues:
- Panic booting the kernel/rootfs from an SD card on Rockchip RK3566
- Panic booting the kernel/rootfs from an SD card on StarFive JH7100
- "swiotlb buffer is full" and data corruption on StarFive JH7110

At this stage no fix have been found, so it's probably better to just
revert the change.

This reverts commit 8396c793ffdf28bb8aee7cfe0891080f8cab7890.

## References
- https://git.kernel.org/stable/c/00bff71745bc3583bd5ca59be91e0ee1d27f1944
- https://git.kernel.org/stable/c/1635e407a4a64d08a8517ac59ca14ad4fc785e75
- https://git.kernel.org/stable/c/47693ba35bccaa16efa465159a1c12d78258349e
- https://git.kernel.org/stable/c/56de724c58c07a7ca3aac027cfd2ccb184ed9e4e
- https://git.kernel.org/stable/c/8f9416147d7ed414109d3501f1cb3d7a1735b25a
- https://git.kernel.org/stable/c/938c13740f8b555986e53c0fcbaf00dcd1fabd4c
- https://git.kernel.org/stable/c/a4685366f07448420badb710ff5c12aaaadf63ad
- https://git.kernel.org/stable/c/f701eb601470bfc0a551913ce5f6ebaa770f0ce0
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53127.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53127
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
