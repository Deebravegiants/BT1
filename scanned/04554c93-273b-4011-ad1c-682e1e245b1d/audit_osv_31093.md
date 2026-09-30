# [M] iio: adc: ti-ads1298: Add NULL check in ads1298_init

## Summary
Severity: Medium
Advisory: CVE-2024-57944
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-57944
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: ti-ads1298: Add NULL check in ads1298_init

devm_kasprintf() can return a NULL pointer on failure. A check on the
return value of such a call in ads1298_init() is missing. Add it.

## References
- https://git.kernel.org/stable/c/69b680bbac9bd611aaa308769d6c71e3e70eb3c3
- https://git.kernel.org/stable/c/bcb394bb28e55312cace75362b8e489eb0e02a30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57944.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57944
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
