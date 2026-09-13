# [M] clk: mediatek: clk-mt6765: Add check for mtk_alloc_clk_data

## Summary
Severity: Medium
Advisory: CVE-2023-52870
Ecosystem: Linux
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52870
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: mediatek: clk-mt6765: Add check for mtk_alloc_clk_data

Add the check for the return value of mtk_alloc_clk_data() in order to
avoid NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/10cc81124407d862f0f747db4baa9c006510b480
- https://git.kernel.org/stable/c/2617aa8ceaf30e41d3eb7f5fef3445542bef193a
- https://git.kernel.org/stable/c/533ca5153ad6c7b7d47ae0114b14d0333964b946
- https://git.kernel.org/stable/c/b5ff3e89b4e7f46ad2aa0de7e08d18e6f87d71bc
- https://git.kernel.org/stable/c/b82681042724924ae3ba0f2f2eeec217fa31e830
- https://git.kernel.org/stable/c/dd1f30d68fa98eb672c0a259297b761656a9025f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52870.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52870
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
