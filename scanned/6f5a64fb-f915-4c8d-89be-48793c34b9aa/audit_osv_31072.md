# [H] iio: light: bh1745: fix information leak in triggered buffer

## Summary
Severity: High
Advisory: CVE-2024-57909
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2024-57909
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: light: bh1745: fix information leak in triggered buffer

The 'scan' local struct is used to push data to user space from a
triggered buffer, but it does not set values for inactive channels, as
it only uses iio_for_each_active_channel() to assign new values.

Initialize the struct to zero before using it to avoid pushing
uninitialized information to userspace.

## References
- https://git.kernel.org/stable/c/1cca2a666e099aa018e5ab385f0a6e01a3053629
- https://git.kernel.org/stable/c/b62fbe3b8eedd3cf3c9ad0b7cb9f72c3f40815f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57909.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57909
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
