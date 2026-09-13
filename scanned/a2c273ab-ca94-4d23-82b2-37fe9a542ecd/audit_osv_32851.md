# [H] iio: adc: ad4851: fix ad4858 chan pointer handling

## Summary
Severity: High
Advisory: CVE-2025-38133
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38133
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: ad4851: fix ad4858 chan pointer handling

The pointer returned from ad4851_parse_channels_common() is incremented
internally as each channel is populated. In ad4858_parse_channels(),
the same pointer was further incremented while setting ext_scan_type
fields for each channel. This resulted in indio_dev->channels being set
to a pointer past the end of the allocated array, potentially causing
memory corruption or undefined behavior.

Fix this by iterating over the channels using an explicit index instead
of incrementing the pointer. This preserves the original base pointer
and ensures all channel metadata is set correctly.

## References
- https://git.kernel.org/stable/c/499a8cee812588905cc940837e69918c1649a19e
- https://git.kernel.org/stable/c/6c3b9e1167d072ce2d01cafec7866647cf8d3616
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38133.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38133
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
