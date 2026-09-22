# [H] i2c: ismt: Fix an out-of-bounds bug in ismt_access()

## Summary
Severity: High
Advisory: CVE-2022-50394
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50394
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: ismt: Fix an out-of-bounds bug in ismt_access()

When the driver does not check the data from the user, the variable
'data->block[0]' may be very large to cause an out-of-bounds bug.

The following log can reveal it:

[   33.995542] i2c i2c-1: ioctl, cmd=0x720, arg=0x7ffcb3dc3a20
[   33.995978] ismt_smbus 0000:00:05.0: I2C_SMBUS_BLOCK_DATA:  WRITE
[   33.996475] ==================================================================
[   33.996995] BUG: KASAN: out-of-bounds in ismt_access.cold+0x374/0x214b
[   33.997473] Read of size 18446744073709551615 at addr ffff88810efcfdb1 by task ismt_poc/485
[   33.999450] Call Trace:
[   34.001849]  memcpy+0x20/0x60
[   34.002077]  ismt_access.cold+0x374/0x214b
[   34.003382]  __i2c_smbus_xfer+0x44f/0xfb0
[   34.004007]  i2c_smbus_xfer+0x10a/0x390
[   34.004291]  i2cdev_ioctl_smbus+0x2c8/0x710
[   34.005196]  i2cdev_ioctl+0x5ec/0x74c

Fix this bug by checking the size of 'data->block[0]' first.

## References
- https://git.kernel.org/stable/c/03b7ef7a6c5ca1ff553470166b4919db88b810f6
- https://git.kernel.org/stable/c/233348a04becf133283f0076e20b317302de21d9
- https://git.kernel.org/stable/c/39244cc754829bf707dccd12e2ce37510f5b1f8d
- https://git.kernel.org/stable/c/4a7bb1d93addb2f67e36fed00a53cb7f270d7b7a
- https://git.kernel.org/stable/c/96c12fd0ec74641295e1c3c34dea3dce1b6c3422
- https://git.kernel.org/stable/c/9ac541a0898e8ec187a3fa7024b9701cffae6bf2
- https://git.kernel.org/stable/c/a642469d464b2780a25a49b51ae56623c65eac34
- https://git.kernel.org/stable/c/bfe41d966c860a8ad4c735639d616da270c92735
- https://git.kernel.org/stable/c/cdcbae2c5003747ddfd14e29db9c1d5d7e7c44dd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50394.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50394
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
