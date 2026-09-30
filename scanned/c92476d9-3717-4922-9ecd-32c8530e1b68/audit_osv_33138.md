# [H] iio: adc: ad7173: fix channels index for syscalib_mode

## Summary
Severity: High
Advisory: CVE-2025-39786
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-39786
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: ad7173: fix channels index for syscalib_mode

Fix the index used to look up the channel when accessing the
syscalib_mode attribute. The address field is a 0-based index (same
as scan_index) that it used to access the channel in the
ad7173_channels array throughout the driver. The channels field, on
the other hand, may not match the address field depending on the
channel configuration specified in the device tree and could result
in an out-of-bounds access.

## References
- https://git.kernel.org/stable/c/0eb8d7b25397330beab8ee62c681975b79f37223
- https://git.kernel.org/stable/c/2def1a8691eb43654da0ae0d2fdb3722e20262a5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39786.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39786
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
