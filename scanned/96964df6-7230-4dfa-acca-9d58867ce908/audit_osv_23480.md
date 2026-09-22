# [H] iio: adc: tsc2046: fix memory corruption by preventing array overflow

## Summary
Severity: High
Advisory: CVE-2022-48927
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2022-48927
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.26, >=5.16.0 <5.16.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: tsc2046: fix memory corruption by preventing array overflow

On one side we have indio_dev->num_channels includes all physical channels +
timestamp channel. On other side we have an array allocated only for
physical channels. So, fix memory corruption by ARRAY_SIZE() instead of
num_channels variable.

Note the first case is a cleanup rather than a fix as the software
timestamp channel bit in active_scanmask is never set by the IIO core.

## References
- https://git.kernel.org/stable/c/082d2c047b0d305bb0b6e9f9d671a09470e2db2d
- https://git.kernel.org/stable/c/0cb9b2f73c182d242a640e512f4785c7c504512f
- https://git.kernel.org/stable/c/b7a78a8adaa8849c02f174d707aead0f85dca0da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48927.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48927
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
