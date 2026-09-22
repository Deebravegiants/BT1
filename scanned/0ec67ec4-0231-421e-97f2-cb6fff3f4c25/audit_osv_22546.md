# [M] CVE-2022-3114

## Summary
Severity: Medium
Advisory: CVE-2022-3114
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-3114
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.16-rc6. imx_register_uart_clocks in drivers/clk/imx/clk.c lacks check of the return value of kcalloc() and will cause the null pointer dereference.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?h=v5.19-rc2&id=ed713e2bc093239ccd380c2ce8ae9e4162f5c037
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3114.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3114
- https://bugzilla.redhat.com/show_bug.cgi?id=2153054
