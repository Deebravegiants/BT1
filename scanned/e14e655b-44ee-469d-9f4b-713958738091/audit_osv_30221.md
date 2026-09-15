# [M] iio: light: veml6030: fix IIO device retrieval from embedded device

## Summary
Severity: Medium
Advisory: CVE-2024-50198
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50198
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.228, >=5.11.0 <5.15.169, >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: light: veml6030: fix IIO device retrieval from embedded device

The dev pointer that is received as an argument in the
in_illuminance_period_available_show function references the device
embedded in the IIO device, not in the i2c client.

dev_to_iio_dev() must be used to accessthe right data. The current
implementation leads to a segmentation fault on every attempt to read
the attribute because indio_dev gets a NULL assignment.

This bug has been present since the first appearance of the driver,
apparently since the last version (V6) before getting applied. A
constant attribute was used until then, and the last modifications might
have not been tested again.

## References
- https://git.kernel.org/stable/c/2cbb41abae65626736b8b52cf3b9339612c5a86a
- https://git.kernel.org/stable/c/50039aec43a82ad2495f2d0fb0c289c8717b4bb2
- https://git.kernel.org/stable/c/905166531831beb067fffe2bdfc98031ffe89087
- https://git.kernel.org/stable/c/bcb90518ccd9e10bf6ab29e31994aab93e4a4361
- https://git.kernel.org/stable/c/bf3ab8e1c28f10df0823d4ff312f83c952b06a15
- https://git.kernel.org/stable/c/c7c44e57750c31de43906d97813273fdffcf7d02
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50198.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50198
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
