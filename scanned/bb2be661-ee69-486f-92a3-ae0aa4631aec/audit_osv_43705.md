# [H] Revert "thermal/drivers/hwmon: Cleanup coding style a bit"

## Summary
Severity: High
Advisory: CVE-2026-74604
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74604
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "thermal/drivers/hwmon: Cleanup coding style a bit"

Revert commit 030a48b0f6ce ("thermal/drivers/hwmon: Cleanup coding style
a bit") that introduced a use-after-free into the error path of
thermal_add_hwmon_sysfs() by removing a valid check from it.

## References
- https://git.kernel.org/stable/c/2434f4765da8ccd7ef31be88b86f1bfa2e95be11
- https://git.kernel.org/stable/c/6a48ee9a5bda0f8ee501f9bef159fb9f39ff519a
- https://git.kernel.org/stable/c/6b446d335ba16e93a266dd77adf1ba51abc82df4
- https://git.kernel.org/stable/c/8d34019d1413629a434a7e8d9f91c76d256196a0
- https://git.kernel.org/stable/c/999e573212d5f1debf073c68be35e55bbfad12fc
- https://git.kernel.org/stable/c/b4c01ae6dd56d9dfd96bd1b29c28afa8fa06b366
- https://git.kernel.org/stable/c/ff8da20b6f47c48d46e47f93f7a59e2d56ee9107
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74604.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74604
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
