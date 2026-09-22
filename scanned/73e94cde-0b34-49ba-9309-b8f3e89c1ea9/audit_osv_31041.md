# [M] phy: rockchip: samsung-hdptx: Set drvdata before enabling runtime PM

## Summary
Severity: Medium
Advisory: CVE-2024-57799
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57799
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

phy: rockchip: samsung-hdptx: Set drvdata before enabling runtime PM

In some cases, rk_hdptx_phy_runtime_resume() may be invoked before
platform_set_drvdata() is executed in ->probe(), leading to a NULL
pointer dereference when using the return of dev_get_drvdata().

Ensure platform_set_drvdata() is called before devm_pm_runtime_enable().

## References
- https://git.kernel.org/stable/c/7061849a4a1752a06944a819dd1f7bfd58df7383
- https://git.kernel.org/stable/c/9d23e48654620fdccfcc74cc2cef04eaf7353d07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57799.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57799
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
