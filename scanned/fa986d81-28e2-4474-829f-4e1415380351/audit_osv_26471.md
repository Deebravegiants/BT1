# [M] clk: imx: clk-imx8mn: fix memory leak in imx8mn_clocks_probe

## Summary
Severity: Medium
Advisory: CVE-2023-53249
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53249
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: imx: clk-imx8mn: fix memory leak in imx8mn_clocks_probe

Use devm_of_iomap() instead of of_iomap() to automatically handle
the unused ioremap region.

If any error occurs, regions allocated by kzalloc() will leak,
but using devm_kzalloc() instead will automatically free the memory
using devm_kfree().

## References
- https://git.kernel.org/stable/c/188d070de9132667956f5aadd98d2bd87d3eac89
- https://git.kernel.org/stable/c/294321349bd3b0680847fc2bbe66b9ab3e522fea
- https://git.kernel.org/stable/c/50b5ddde8fad5f0ffd239029d0956af633a0f9b1
- https://git.kernel.org/stable/c/9428cf0fbf4be9a24f3e15a0c166b861b12666af
- https://git.kernel.org/stable/c/9ba3693b0350b154fdd7830559bbc7b04c067096
- https://git.kernel.org/stable/c/d4fa5e47af1e7bb2bbcaac062b14216c00e92148
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53249.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53249
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
