# [H] i2c: s3c24xx: check the size of the SMBUS message before using it

## Summary
Severity: High
Advisory: CVE-2026-31627
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31627
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: s3c24xx: check the size of the SMBUS message before using it

The first byte of an i2c SMBUS message is the size, and it should be
verified to ensure that it is in the range of 0..I2C_SMBUS_BLOCK_MAX
before processing it.

This is the same logic that was added in commit a6e04f05ce0b ("i2c:
tegra: check msg length in SMBUS block read") to the i2c tegra driver.

## References
- https://git.kernel.org/stable/c/2d262da4bca6fab96e2e709feb95b31b0a9a03a7
- https://git.kernel.org/stable/c/377fae22a137b6b89f3f32399a58c52cf2325416
- https://git.kernel.org/stable/c/71b3c316b22c555d2769126a92b1244b15a9750d
- https://git.kernel.org/stable/c/8f756a5964396da0fc9e0db33253a5b85dbbcbb6
- https://git.kernel.org/stable/c/aaaaec39ddbcd06770dca7f1adebc3b1242ebe7b
- https://git.kernel.org/stable/c/c0128c7157d639a931353ea344fb44aad6d6e17a
- https://git.kernel.org/stable/c/d87d5620125a03b1eadbd5df39748215d3db7ddb
- https://git.kernel.org/stable/c/fa00738ab30b07db1a43b9c85fc56b8cc3b7d197
- https://git.kernel.org/stable/c/fd1650da24ed54c716aa9b69e9bbd8a662e492da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31627.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31627
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
