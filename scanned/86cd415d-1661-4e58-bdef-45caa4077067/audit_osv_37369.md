# [H] net/x25: Fix overflow when accumulating packets

## Summary
Severity: High
Advisory: CVE-2026-31417
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-31417
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/x25: Fix overflow when accumulating packets

Add a check to ensure that `x25_sock.fraglen` does not overflow.

The `fraglen` also needs to be resetted when purging `fragment_queue` in
`x25_clear_queues()`.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1734bd85c5e0a7a801295b729efb56b009cb8fc3
- https://git.kernel.org/stable/c/4e2d1bcef78d21247fe8fef13bc7ed95885df2b5
- https://git.kernel.org/stable/c/6e568835ea54a3e1d08e310e34f95d434e739477
- https://git.kernel.org/stable/c/798d613afb64b01a203f448fb0f43c37c6afe79d
- https://git.kernel.org/stable/c/8c92969c197b91c134be27dc3afb64ab468853a9
- https://git.kernel.org/stable/c/96fc16370b0bceb289c7e0479bd0540b81e257aa
- https://git.kernel.org/stable/c/a1822cb524e89b4cd2cf0b82e484a2335496a6d9
- https://git.kernel.org/stable/c/f953f11ccf4afe6feb635c08145f4240d9a6b544
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31417.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31417
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
