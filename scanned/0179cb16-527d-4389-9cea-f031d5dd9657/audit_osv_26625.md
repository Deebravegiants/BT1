# [M] media: platform: mediatek: vpu: fix NULL ptr dereference

## Summary
Severity: Medium
Advisory: CVE-2023-53425
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53425
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <4.14.324, >=4.15.0 <4.19.293, >=4.20.0 <5.4.255, >=5.5.0 <5.10.192, >=5.11.0 <5.15.128, >=5.16.0 <6.1.47, >=6.2.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: platform: mediatek: vpu: fix NULL ptr dereference

If pdev is NULL, then it is still dereferenced.

This fixes this smatch warning:

drivers/media/platform/mediatek/vpu/mtk_vpu.c:570 vpu_load_firmware() warn: address of NULL pointer 'pdev'

## References
- https://git.kernel.org/stable/c/099e929e7477f37ca16738fc158d7101c0189ca1
- https://git.kernel.org/stable/c/1b3f25d3894a091abc247eadab266a2c9be64389
- https://git.kernel.org/stable/c/2caeb722f0ea5d2d24af30bb1753a89d449b6aa0
- https://git.kernel.org/stable/c/3df55cd773e8603b623425cc97b05e542854ad27
- https://git.kernel.org/stable/c/4d299e6e0ac3cf8ab4517dc29c9294bc4bf72398
- https://git.kernel.org/stable/c/776b34615a29551d69d82a0082e7319d5ea284bd
- https://git.kernel.org/stable/c/b7bd48f0be84e24d21aa3a8f59a8a9cb8633a1c4
- https://git.kernel.org/stable/c/c1c5826223ae05a48d21f6708c6f34ee9006238c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53425.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53425
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
