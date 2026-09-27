# [M] HID: betop: check shape of output reports

## Summary
Severity: Medium
Advisory: CVE-2023-53015
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53015
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <4.14.305, >=4.15.0 <4.19.272, >=4.20.0 <5.4.231, >=5.5.0 <5.10.166, >=5.11.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: betop: check shape of output reports

betopff_init() only checks the total sum of the report counts for each
report field to be at least 4, but hid_betopff_play() expects 4 report
fields.
A device advertising an output report with one field and 4 report counts
would pass the check but crash the kernel with a NULL pointer dereference
in hid_betopff_play().

## References
- https://git.kernel.org/stable/c/07bc32e53c7bd5c91472cc485231ef6274db9b76
- https://git.kernel.org/stable/c/1a2a47b85cab50a3c146731bfeaf2d860f5344ee
- https://git.kernel.org/stable/c/28fc6095da22dc88433d79578ae1c495ebe8ca43
- https://git.kernel.org/stable/c/3782c0d6edf658b71354a64d60aa7a296188fc90
- https://git.kernel.org/stable/c/7317326f685824c7c29bd80841fd18041af6bb73
- https://git.kernel.org/stable/c/d3065cc56221d1a5eda237e94eaf2a627b88ab79
- https://git.kernel.org/stable/c/dbab4dba400d6ea9a9697fbbd287adbf7db1dac4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53015.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53015
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
