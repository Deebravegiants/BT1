# [H] iio: adc: ti-ads1119: fix information leak in triggered buffer

## Summary
Severity: High
Advisory: CVE-2024-57905
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2024-57905
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: ti-ads1119: fix information leak in triggered buffer

The 'scan' local struct is used to push data to user space from a
triggered buffer, but it has a hole between the sample (unsigned int)
and the timestamp. This hole is never initialized.

Initialize the struct to zero before using it to avoid pushing
uninitialized information to userspace.

## References
- https://git.kernel.org/stable/c/2f1687cca911a2f294313c762e0646cd9e7be8cc
- https://git.kernel.org/stable/c/75f339d3ecd38cb1ce05357d647189d4a7f7ed08
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57905.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57905
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
