# [M] iio: adc: ad7124: fix division by zero in ad7124_set_channel_odr()

## Summary
Severity: Medium
Advisory: CVE-2024-50232
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50232
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: ad7124: fix division by zero in ad7124_set_channel_odr()

In the ad7124_write_raw() function, parameter val can potentially
be zero. This may lead to a division by zero when DIV_ROUND_CLOSEST()
is called within ad7124_set_channel_odr(). The ad7124_write_raw()
function is invoked through the sequence: iio_write_channel_raw() ->
iio_write_channel_attribute() -> iio_channel_write(), with no checks
in place to ensure val is non-zero.

## References
- https://git.kernel.org/stable/c/0ac0beb4235a9a474f681280a3bd4e2a5bb66569
- https://git.kernel.org/stable/c/3dc0eda2cd5c653b162852ae5f0631bfe4ca5e95
- https://git.kernel.org/stable/c/4f588fffc307a4bc2761aee6ff275bb4b433e451
- https://git.kernel.org/stable/c/efa353ae1b0541981bc96dbf2e586387d0392baa
- https://git.kernel.org/stable/c/f51343f346e6abde094548a7fb34472b0d4cae91
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50232.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50232
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
