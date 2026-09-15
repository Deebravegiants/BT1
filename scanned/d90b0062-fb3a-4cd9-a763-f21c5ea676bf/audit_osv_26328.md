# [M] clk: mediatek: clk-mt7629: Add check for mtk_alloc_clk_data

## Summary
Severity: Medium
Advisory: CVE-2023-52858
Ecosystem: Linux
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52858
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.261, >=5.5.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: mediatek: clk-mt7629: Add check for mtk_alloc_clk_data

Add the check for the return value of mtk_alloc_clk_data() in order to
avoid NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/1d89430fc3158f872d492f1b88d07262f48290c0
- https://git.kernel.org/stable/c/2befa515c1bb6cdd33c262b909d93d1973a219aa
- https://git.kernel.org/stable/c/4f861b63945e076f9f003a5fad958174096df1ee
- https://git.kernel.org/stable/c/5fbea47eebff5daeca7d918c99289bcd3ae4dc8d
- https://git.kernel.org/stable/c/a836efc21ef04608333d6d05753e558ebd1f85d0
- https://git.kernel.org/stable/c/e8ae4b49dd9cfde69d8de8c0c0cd7cf1b004482e
- https://git.kernel.org/stable/c/e964d21dc034b650d719c4ea39564bec72b42f94
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52858.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52858
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
