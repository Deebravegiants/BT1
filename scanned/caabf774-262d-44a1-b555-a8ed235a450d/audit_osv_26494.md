# [H] clk: mediatek: mt8183: Add back SSPM related clocks

## Summary
Severity: High
Advisory: CVE-2023-53274
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53274
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.4.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: mediatek: mt8183: Add back SSPM related clocks

This reverts commit 860690a93ef23b567f781c1b631623e27190f101.

On the MT8183, the SSPM related clocks were removed claiming a lack of
usage. This however causes some issues when the driver was converted to
the new simple-probe mechanism. This mechanism allocates enough space
for all the clocks defined in the clock driver, not the highest index
in the DT binding. This leads to out-of-bound writes if their are holes
in the DT binding or the driver (due to deprecated or unimplemented
clocks). These errors can go unnoticed and cause memory corruption,
leading to crashes in unrelated areas, or nothing at all. KASAN will
detect them.

Add the SSPM related clocks back to the MT8183 clock driver to fully
implement the DT binding. The SSPM clocks are for the power management
co-processor, and should never be turned off. They are marked as such.

## References
- https://git.kernel.org/stable/c/1eb8d61ac5c9c7ec56bb96d433532807509b9288
- https://git.kernel.org/stable/c/45d69917a4af6c869193f95932dc6d6f15d5ef86
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53274.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53274
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
