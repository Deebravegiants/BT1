# [H] iio: gyro: mpu3050: Move iio_device_register() to correct location

## Summary
Severity: High
Advisory: CVE-2026-31761
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31761
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: gyro: mpu3050: Move iio_device_register() to correct location

iio_device_register() should be at the end of the probe function to
prevent race conditions.

Place iio_device_register() at the end of the probe function and place
iio_device_unregister() accordingly.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/051ca43b0e0e4b66bfd349cd53ccf231ad1d69b7
- https://git.kernel.org/stable/c/22487ef85f6dd9499ddf49b85a08afc50a3f1992
- https://git.kernel.org/stable/c/2a4537653d200fda2a8516083459f8ff6194f8fc
- https://git.kernel.org/stable/c/4c05799449108fb0e0a6bd30e65fffc71e60db4d
- https://git.kernel.org/stable/c/59a317f8215674c8330817770497301bfb2c1b99
- https://git.kernel.org/stable/c/92f18aa86302fe83e0726a1191015f427d4ff056
- https://git.kernel.org/stable/c/caec338f91469f0a70b68165185afa3abc994545
- https://git.kernel.org/stable/c/cc3de12a5612ee25df7fb549cb7b3e4cc8bfaf9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31761.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31761
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
