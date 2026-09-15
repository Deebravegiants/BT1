# [H] mailbox: mtk-cmdq: fix wrong use of sizeof in cmdq_get_clocks()

## Summary
Severity: High
Advisory: CVE-2024-56684
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56684
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mailbox: mtk-cmdq: fix wrong use of sizeof in cmdq_get_clocks()

It should be size of the struct clk_bulk_data, not data pointer pass to
devm_kcalloc().

## References
- https://git.kernel.org/stable/c/271ee263cc8771982809185007181ca10346fe73
- https://git.kernel.org/stable/c/31986fad0cfdda8d8893230da04f5eb0774854d9
- https://git.kernel.org/stable/c/a9c7cb960fc6e056ebecebd136a127612b15630d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56684.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56684
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
