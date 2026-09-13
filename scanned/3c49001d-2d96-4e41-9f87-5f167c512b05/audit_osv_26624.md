# [M] clk: mediatek: fix of_iomap memory leak

## Summary
Severity: Medium
Advisory: CVE-2023-53424
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53424
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.164, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: mediatek: fix of_iomap memory leak

Smatch reports:
drivers/clk/mediatek/clk-mtk.c:583 mtk_clk_simple_probe() warn:
    'base' from of_iomap() not released on lines: 496.

This problem was also found in linux-next. In mtk_clk_simple_probe(),
base is not released when handling errors
if clk_data is not existed, which may cause a leak.
So free_base should be added here to release base.

## References
- https://git.kernel.org/stable/c/2cae6a28d8c12c597e8656962271520434c61c48
- https://git.kernel.org/stable/c/3db7285e044144fd88a356f5b641b9cd4b231a77
- https://git.kernel.org/stable/c/47234e19b00816a8a7b278c7173f6d4e928c43c7
- https://git.kernel.org/stable/c/847d5dd788ce05f0aaaa36ea174f7f0b9cf86f7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53424.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53424
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
