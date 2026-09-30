# [H] tipc: fix memory leak in tipc_link_xmit

## Summary
Severity: High
Advisory: CVE-2025-37757
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-37757
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.4.293, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix memory leak in tipc_link_xmit

In case the backlog transmit queue for system-importance messages is overloaded,
tipc_link_xmit() returns -ENOBUFS but the skb list is not purged. This leads to
memory leak and failure when a skb is allocated.

This commit fixes this issue by purging the skb list before tipc_link_xmit()
returns.

## References
- https://git.kernel.org/stable/c/09c2dcda2c551bba30710c33f6ac678ae7395389
- https://git.kernel.org/stable/c/24e6280cdd7f8d01fc6b9b365fb800c2fb7ea9bb
- https://git.kernel.org/stable/c/69ae94725f4fc9e75219d2d69022029c5b24bc9a
- https://git.kernel.org/stable/c/7c5957f7905b4aede9d7a559d271438f3ca9e852
- https://git.kernel.org/stable/c/84895f5ce3829d9fc030e5ec2d8729da4c0c9d08
- https://git.kernel.org/stable/c/a40cbfbb8f95c325430f017883da669b2aa927d4
- https://git.kernel.org/stable/c/d0e02d3d27a0b4dcb13f954f537ca1dd8f282dcf
- https://git.kernel.org/stable/c/d4d40e437adb376be16b3a12dd5c63f0fa768247
- https://git.kernel.org/stable/c/ed06675d3b8cd37120b447646d53f7cd3e6fcd63
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37757.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37757
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
