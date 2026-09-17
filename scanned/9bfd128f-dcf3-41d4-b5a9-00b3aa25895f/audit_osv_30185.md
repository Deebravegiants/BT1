# [H] firmware: arm_scmi: Fix the double free in scmi_debugfs_common_setup()

## Summary
Severity: High
Advisory: CVE-2024-50159
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50159
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: arm_scmi: Fix the double free in scmi_debugfs_common_setup()

Clang static checker(scan-build) throws below warning：
  |  drivers/firmware/arm_scmi/driver.c:line 2915, column 2
  |        Attempt to free released memory.

When devm_add_action_or_reset() fails, scmi_debugfs_common_cleanup()
will run twice which causes double free of 'dbg->name'.

Remove the redundant scmi_debugfs_common_cleanup() to fix this problem.

## References
- https://git.kernel.org/stable/c/39b13dce1a91cdfc3bec9238f9e89094551bd428
- https://git.kernel.org/stable/c/6d91d07913aee90556362d648d6a28a1eda419dc
- https://git.kernel.org/stable/c/fb324fdaf546bf14bc4c17e0037bca6cb952b121
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50159.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50159
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
