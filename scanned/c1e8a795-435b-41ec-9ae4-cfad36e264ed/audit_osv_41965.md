# [H] i2c: stub: Reject I2C block transfers with invalid length

## Summary
Severity: High
Advisory: CVE-2026-64191
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-64191
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.37, >=6.19.0 <7.0.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: stub: Reject I2C block transfers with invalid length

The I2C_SMBUS_I2C_BLOCK_DATA case in stub_xfer() uses data->block[0]
as the transfer length. The existing check only clamps it to avoid
overrunning the chip->words[256] register array, but does not validate
it against I2C_SMBUS_BLOCK_MAX (32), which is the limit of the union
i2c_smbus_data.block buffer (34 bytes total). The driver is a
development/test tool (CONFIG_I2C_STUB=m, not built by default)
that must be loaded with a chip_addr= parameter.

A local user with access to /dev/i2c-* can issue an I2C_SMBUS ioctl
with I2C_SMBUS_I2C_BLOCK_DATA and data->block[0] > 32, causing
stub_xfer() to read or write past the end of the union
i2c_smbus_data.block buffer:

 BUG: KASAN: stack-out-of-bounds in stub_xfer (drivers/i2c/i2c-stub.c:223)
 Read of size 1 at addr ffff88800abcfd92 by task exploit/81
 Call Trace:
  <TASK>
  stub_xfer (drivers/i2c/i2c-stub.c:223)
  __i2c_smbus_xfer (drivers/i2c/i2c-core-smbus.c:593)
  i2c_smbus_xfer (drivers/i2c/i2c-core-smbus.c:536)
  i2cdev_ioctl_smbus (drivers/i2c/i2c-dev.c:391)
  i2cdev_ioctl (drivers/i2c/i2c-dev.c:478)
  __x64_sys_ioctl (fs/ioctl.c:583)
  do_syscall_64 (arch/x86/entry/syscall_64.c:94)
  entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:130)
  </TASK>

The bug exists because i2c-stub implements .smbus_xfer directly,
bypassing the I2C_SMBUS_BLOCK_MAX validation in
i2c_smbus_xfer_emulated(). The I2C_SMBUS_BLOCK_DATA case in the same
function correctly validates against I2C_SMBUS_BLOCK_MAX, but the
I2C_SMBUS_I2C_BLOCK_DATA case does not.

Fix by rejecting transfers with data->block[0] == 0 or
data->block[0] > I2C_SMBUS_BLOCK_MAX with -EINVAL, consistent with
both the I2C_SMBUS_BLOCK_DATA case in the same function and the
I2C_SMBUS_I2C_BLOCK_DATA validation in i2c_smbus_xfer_emulated().

## References
- https://git.kernel.org/stable/c/0526931b16e5a118d367b7bfce7d797e63f7ac69
- https://git.kernel.org/stable/c/1c4ffe6b4f04365485ed58d64c9bb86b46fc9037
- https://git.kernel.org/stable/c/21e87f336ac6303fed54a69b1d0d79a23b25c8d0
- https://git.kernel.org/stable/c/3fd225f3e4cd67ec8ddab1afed9da03c7c43537c
- https://git.kernel.org/stable/c/4bd8635f28c135a08aac6badcd7d9b5cdb34335f
- https://git.kernel.org/stable/c/5f4d2bd028ebb6e4c09a9d64842546022321d4a7
- https://git.kernel.org/stable/c/6036b5067a8199ba7a2dc7b377d4b9dd276d5f9e
- https://git.kernel.org/stable/c/7e9072dbd5f2f17934751873450d2c22080ead80
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64191.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64191
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
