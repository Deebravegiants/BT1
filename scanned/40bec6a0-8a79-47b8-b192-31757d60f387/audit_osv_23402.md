# [H] regmap: spi: Reserve space for register address/padding

## Summary
Severity: High
Advisory: CVE-2022-48696
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2022-48696
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

regmap: spi: Reserve space for register address/padding

Currently the max_raw_read and max_raw_write limits in regmap_spi struct
do not take into account the additional size of the transmitted register
address and padding.  This may result in exceeding the maximum permitted
SPI message size, which could cause undefined behaviour, e.g. data
corruption.

Fix regmap_get_spi_bus() to properly adjust the above mentioned limits
by reserving space for the register address/padding as set in the regmap
configuration.

## References
- https://git.kernel.org/stable/c/15ff1f17847c19174b260bd7dd0de33edcebd45e
- https://git.kernel.org/stable/c/f5723cfc01932c7a8d5c78dbf7e067e537c91439
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48696.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48696
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
