# [H] nvmet-fc: avoid deadlock on delete association path

## Summary
Severity: High
Advisory: CVE-2024-26769
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26769
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-fc: avoid deadlock on delete association path

When deleting an association the shutdown path is deadlocking because we
try to flush the nvmet_wq nested. Avoid this by deadlock by deferring
the put work into its own work item.

## References
- https://git.kernel.org/stable/c/1d86f79287206deec36d63b89c741cf542b6cadd
- https://git.kernel.org/stable/c/5e0bc09a52b6169ce90f7ac6e195791adb16cec4
- https://git.kernel.org/stable/c/710c69dbaccdac312e32931abcb8499c1525d397
- https://git.kernel.org/stable/c/9e6987f8937a7bd7516aa52f25cb7e12c0c92ee8
- https://git.kernel.org/stable/c/eaf0971fdabf2a93c1429dc6bedf3bbe85dffa30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26769.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26769
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
