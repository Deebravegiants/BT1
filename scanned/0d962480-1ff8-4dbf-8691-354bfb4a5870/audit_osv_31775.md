# [H] ndisc: extend RCU protection in ndisc_send_skb()

## Summary
Severity: High
Advisory: CVE-2025-21760
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21760
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ndisc: extend RCU protection in ndisc_send_skb()

ndisc_send_skb() can be called without RTNL or RCU held.

Acquire rcu_read_lock() earlier, so that we can use dev_net_rcu()
and avoid a potential UAF.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/04e05112f10354ffc3bb6cc796d553bab161594c
- https://git.kernel.org/stable/c/10a1f3fece2f0d23a3a618b72b2b4e6f408ef7d1
- https://git.kernel.org/stable/c/4d576202b90b1b95a7c428a80b536f91b8201bcc
- https://git.kernel.org/stable/c/789230e5a8c1097301afc802e242c79bc8835c67
- https://git.kernel.org/stable/c/a9319d800b5701e7f5e3fa71a5b7c4831fc20d6d
- https://git.kernel.org/stable/c/ae38982f521621c216fc2f5182cd091f4734641d
- https://git.kernel.org/stable/c/e24d225e4cb8cf108bde00b76594499b98f0a74d
- https://git.kernel.org/stable/c/ed6ae1f325d3c43966ec1b62ac1459e2b8e45640
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21760.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21760
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
