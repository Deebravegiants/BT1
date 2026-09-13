# [M] net/sctp: Prevent autoclose integer overflow in sctp_association_init()

## Summary
Severity: Medium
Advisory: CVE-2024-57938
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-57938
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.4.289, >=5.5.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.124, >=6.2.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sctp: Prevent autoclose integer overflow in sctp_association_init()

While by default max_autoclose equals to INT_MAX / HZ, one may set
net.sctp.max_autoclose to UINT_MAX. There is code in
sctp_association_init() that can consequently trigger overflow.

## References
- https://git.kernel.org/stable/c/081bdb3a31674339313c6d702af922bc29de2c53
- https://git.kernel.org/stable/c/2297890b778b0e7c8200d6818154f7e461d78e94
- https://git.kernel.org/stable/c/271f031f4c31c07e2a85a1ba2b4c8e734909a477
- https://git.kernel.org/stable/c/4e86729d1ff329815a6e8a920cb554a1d4cb5b8d
- https://git.kernel.org/stable/c/7af63ef5fe4d480064eb22583b24ffc8b408183a
- https://git.kernel.org/stable/c/94b7ed0a4896420988e1776942f0a3f67167873e
- https://git.kernel.org/stable/c/f9c3adb083d3278f065a83c3f667f1246c74c31f
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57938.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57938
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
