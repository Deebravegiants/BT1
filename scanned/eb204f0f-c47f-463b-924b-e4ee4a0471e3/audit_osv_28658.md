# [H] net: bcmasp: fix memory leak when bringing down interface

## Summary
Severity: High
Advisory: CVE-2024-35858
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35858
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bcmasp: fix memory leak when bringing down interface

When bringing down the TX rings we flush the rings but forget to
reclaimed the flushed packets. This leads to a memory leak since we
do not free the dma mapped buffers. This also leads to tx control
block corruption when bringing down the interface for power
management.

## References
- https://git.kernel.org/stable/c/09040baf8779ad880e0e0d0ea10e57aa929ef3ab
- https://git.kernel.org/stable/c/2389ad1990163d29cba5480d693b4c2e31cc545c
- https://git.kernel.org/stable/c/9f898fc2c31fbf0ac5ecd289f528a716464cb005
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35858.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35858
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
