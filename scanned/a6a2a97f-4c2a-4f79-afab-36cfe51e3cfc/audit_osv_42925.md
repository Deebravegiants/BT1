# [H] mtd: rawnand: fix condition in 'nand_select_target()'

## Summary
Severity: High
Advisory: CVE-2026-72165
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72165
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: rawnand: fix condition in 'nand_select_target()'

'cs' here must be in range [0:nanddev_ntargets[.

## References
- https://git.kernel.org/stable/c/3da4eb15c7b421c2d97c402bb7bd607c44822995
- https://git.kernel.org/stable/c/483a8a8581ee1274ec70e2561492096d4a7305e6
- https://git.kernel.org/stable/c/4bbfcf9c7e46cae58257150bf834853559382e28
- https://git.kernel.org/stable/c/8507c2cc9e4fa402401819f44d1e8a5ef4d11d8b
- https://git.kernel.org/stable/c/8f575fc17360827ca1d1940a84f3c7ee40407a10
- https://git.kernel.org/stable/c/c2a131fb6882c98aada739479cc96df8748d0c24
- https://git.kernel.org/stable/c/e6df4fea1dc86c058e1918136c9b9d8e80c4be1b
- https://git.kernel.org/stable/c/fbc7c8a1167b2eb56b2fd8598c29a3d5e9f8676e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72165.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72165
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
