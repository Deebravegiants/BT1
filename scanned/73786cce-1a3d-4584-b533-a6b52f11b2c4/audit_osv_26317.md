# [H] wifi: ath12k: fix possible out-of-bound write in ath12k_wmi_ext_hal_reg_caps()

## Summary
Severity: High
Advisory: CVE-2023-52829
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52829
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix possible out-of-bound write in ath12k_wmi_ext_hal_reg_caps()

reg_cap.phy_id is extracted from WMI event and could be an unexpected value
in case some errors happen. As a result out-of-bound write may occur to
soc->hal_reg_cap. Fix it by validating reg_cap.phy_id before using it.

This is found during code review.

Compile tested only.

## References
- https://git.kernel.org/stable/c/4dd0547e8b45faf6f95373be5436b66cde326c0e
- https://git.kernel.org/stable/c/b302dce3d9edea5b93d1902a541684a967f3c63c
- https://git.kernel.org/stable/c/dfe13eaab043130f90dd3d57c7d88577c04adc97
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52829.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52829
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
