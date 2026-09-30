# [H] iio: adc: ad7923: Fix buffer overflow for tx_buf and ring_xfer

## Summary
Severity: High
Advisory: CVE-2024-56557
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56557
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.15.203, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: ad7923: Fix buffer overflow for tx_buf and ring_xfer

The AD7923 was updated to support devices with 8 channels, but the size
of tx_buf and ring_xfer was not increased accordingly, leading to a
potential buffer overflow in ad7923_update_scan_mode().

## References
- https://git.kernel.org/stable/c/00663d3e000c31d0d49ef86a809f5c107c2d09cd
- https://git.kernel.org/stable/c/218ecc35949129171ca39bcc0d407c8dc4cd0bbc
- https://git.kernel.org/stable/c/3a4187ec454e19903fd15f6e1825a4b84e59a4cd
- https://git.kernel.org/stable/c/6e4d236d9c4b38571c394d3ab6e85dfb71c33ed3
- https://git.kernel.org/stable/c/e5cac32721997cb8bcb208a29f4598b3faf46338
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56557.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56557
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
