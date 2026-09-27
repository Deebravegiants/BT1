# [H] iio: pressure: mprls0025pa: fix spi_transfer struct initialisation

## Summary
Severity: High
Advisory: CVE-2026-46326
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46326
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: pressure: mprls0025pa: fix spi_transfer struct initialisation

Make sure that the spi_transfer struct is zeroed out before use.

## References
- https://git.kernel.org/stable/c/1e0ac56c92e26115cbc8cfc639843725cb3a7d6a
- https://git.kernel.org/stable/c/664ffdf34c01810085e4d85508b361c3fdd2ab40
- https://git.kernel.org/stable/c/72158f9ae29a9e56d0f9704ce461a866feaf9925
- https://git.kernel.org/stable/c/9080c7ac30f5f8f8fcb7b27b56df60fea7909c21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46326.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46326
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
