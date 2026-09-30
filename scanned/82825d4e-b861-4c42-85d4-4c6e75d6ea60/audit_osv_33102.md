# [H] i2c: rtl9300: Fix out-of-bounds bug in rtl9300_i2c_smbus_xfer

## Summary
Severity: High
Advisory: CVE-2025-39680
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39680
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: rtl9300: Fix out-of-bounds bug in rtl9300_i2c_smbus_xfer

The data->block[0] variable comes from user. Without proper check,
the variable may be very large to cause an out-of-bounds bug.

Fix this bug by checking the value of data->block[0] first.

1. commit 39244cc75482 ("i2c: ismt: Fix an out-of-bounds bug in
   ismt_access()")
2. commit 92fbb6d1296f ("i2c: xgene-slimpro: Fix out-of-bounds bug in
   xgene_slimpro_i2c_xfer()")

## References
- https://git.kernel.org/stable/c/071e43fcba5ddd9a7813e6cc0aa10299eae41b21
- https://git.kernel.org/stable/c/57f312b955938fc4663f430cb57a71f2414f601b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39680.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39680
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
