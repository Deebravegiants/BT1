# [H] mtk-sd: Prevent memory corruption from DMA map failure

## Summary
Severity: High
Advisory: CVE-2025-38401
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38401
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.4.296, >=5.5.0 <5.10.240, >=5.11.0 <5.15.187, >=5.16.0 <6.1.144, >=6.2.0 <6.6.97, >=6.7.0 <6.12.37, >=6.13.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtk-sd: Prevent memory corruption from DMA map failure

If msdc_prepare_data() fails to map the DMA region, the request is
not prepared for data receiving, but msdc_start_data() proceeds
the DMA with previous setting.
Since this will lead a memory corruption, we have to stop the
request operation soon after the msdc_prepare_data() fails to
prepare it.

## References
- https://git.kernel.org/stable/c/3419bc6a7b65cbbb91417bb9970208478e034c79
- https://git.kernel.org/stable/c/48bf4f3dfcdab02b22581d8e350a2d23130b72c0
- https://git.kernel.org/stable/c/5ac9e9e2e9cd6247d8c2d99780eae4556049e1cc
- https://git.kernel.org/stable/c/61cdd663564674ea21ceb50aa9d3697cbe9e45f9
- https://git.kernel.org/stable/c/63e8953f16acdcb23e2d4dd8a566d3c34df3e200
- https://git.kernel.org/stable/c/a5f5f67b284d81776d4a3eb1f8607e4b7f91f11c
- https://git.kernel.org/stable/c/d54771571f74a82c59830a32e76af78a8e57ac69
- https://git.kernel.org/stable/c/f5de469990f19569627ea0dd56536ff5a13beaa3
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38401.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38401
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
