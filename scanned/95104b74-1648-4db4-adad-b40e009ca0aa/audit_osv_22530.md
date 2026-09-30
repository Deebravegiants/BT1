# [M] CVE-2022-3111

## Summary
Severity: Medium
Advisory: CVE-2022-3111
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-3111
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.16-rc6. free_charger_irq() in drivers/power/supply/wm8350_power.c lacks free of WM8350_IRQ_CHG_FAST_RDY, which is registered in wm8350_init_charger().

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?h=v5.19-rc2&id=6dee930f6f6776d1e5a7edf542c6863b47d9f078
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3111.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3111
- https://bugzilla.redhat.com/show_bug.cgi?id=2153059
