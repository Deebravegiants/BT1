# [M] tcp: Fix data-races around sysctl_tcp_max_reordering.

## Summary
Severity: Medium
Advisory: CVE-2022-49571
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49571
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix data-races around sysctl_tcp_max_reordering.

While reading sysctl_tcp_max_reordering, it can be changed
concurrently.  Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/064852663308c801861bd54789d81421fa4c2928
- https://git.kernel.org/stable/c/46deb91ac8a790286ad6d24cf92e7ab0ab2582bb
- https://git.kernel.org/stable/c/50a1d3d097503a90cf84ebe120afcde37e9c33b3
- https://git.kernel.org/stable/c/5e38cee24f19d19280c68f1ac8bf6790d607f60a
- https://git.kernel.org/stable/c/a11e5b3e7a59fde1a90b0eaeaa82320495cf8cae
- https://git.kernel.org/stable/c/ce3731c61589ed73364a5b55ce34131762ef9b60
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49571.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49571
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
