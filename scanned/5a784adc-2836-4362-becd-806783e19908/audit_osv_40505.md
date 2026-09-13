# [H] iio: adc: ti-ads1298: add bounds check to pga_settings index

## Summary
Severity: High
Advisory: CVE-2026-53386
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53386
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.95, >=6.13.0 <6.18.37, >=6.19.0 <7.0.14, >=7.1.0 <7.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: ti-ads1298: add bounds check to pga_settings index

ads1298_pga_settings has 7 elements but ADS1298_MASK_CH_PGA can yield
values 0-7. If it yields a value >= 7, this causes an out-of-bounds
array access. Add a bounds check and return -EINVAL if the index
is out of range.

Note that the remaining value b111 is reserved so should not be seen
in a correctly functioning system.

## References
- https://git.kernel.org/stable/c/95e8a48d7a85d4226934020e57815a3316d3a14b
- https://git.kernel.org/stable/c/abd776ded3e256889610595290f6ca46cb6e91ab
- https://git.kernel.org/stable/c/abe0854e356b1bb814393ca884cb42b3eb12ce10
- https://git.kernel.org/stable/c/d08d82d83ed45fd8c001a9df66ad7ebb86c9d6c6
- https://git.kernel.org/stable/c/d5793975fc3b1780ba576812158ef22e3104e60e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53386.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53386
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
