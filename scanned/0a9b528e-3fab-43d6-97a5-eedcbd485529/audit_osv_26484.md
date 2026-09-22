# [M] clk: imx: clk-imxrt1050: fix memory leak in imxrt1050_clocks_probe

## Summary
Severity: Medium
Advisory: CVE-2023-53264
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53264
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: imx: clk-imxrt1050: fix memory leak in imxrt1050_clocks_probe

Use devm_of_iomap() instead of of_iomap() to automatically
handle the unused ioremap region. If any error occurs, regions allocated by
kzalloc() will leak, but using devm_kzalloc() instead will automatically
free the memory using devm_kfree().

Also, fix error handling of hws by adding unregister_hws label, which
unregisters remaining hws when iomap failed.

## References
- https://git.kernel.org/stable/c/02e54db221bb001b32f839e0149ee8d890ab9aa1
- https://git.kernel.org/stable/c/0fbdfd2542252e4c02e8158a06b7c0c9cfd40f99
- https://git.kernel.org/stable/c/1839032251a66f2ae5a043c495532830a55d28c4
- https://git.kernel.org/stable/c/1b280598ab3bd8a2dc8b96a12530d5b1ee7a8f4a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53264.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53264
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
