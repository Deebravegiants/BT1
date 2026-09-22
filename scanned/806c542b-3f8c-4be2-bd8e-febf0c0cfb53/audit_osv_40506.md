# [H] iio: light: veml6075: add bounds check to veml6075_it_ms index

## Summary
Severity: High
Advisory: CVE-2026-53387
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53387
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.95, >=6.13.0 <6.18.37, >=6.19.0 <7.0.14, >=7.1.0 <7.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: light: veml6075: add bounds check to veml6075_it_ms index

veml6075_it_ms has 5 elements but VEML6075_CONF_IT can yield values 0-7.
If it returns a value >= 5, this causes an out-of-bounds array access.
Add a bounds check and return -EINVAL if the index is out of range.

The problem values are reserved so should never be read from the
register. Hence this is hardening against fault device, missprogramming
or bus corruption.

## References
- https://git.kernel.org/stable/c/0a89002737ee34decc20fa232204dbe5fe83e0de
- https://git.kernel.org/stable/c/307dc4240bd41852d9e0912921e298160db1c109
- https://git.kernel.org/stable/c/df9127a1d2d748e426c49c8fcd9b6801e4eb743d
- https://git.kernel.org/stable/c/e545936e06f1c7173ab41a5f33a77ff43ced3a8d
- https://git.kernel.org/stable/c/f75beebcd5bc9bdc80e0722142e78a6f306214ee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53387.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53387
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
