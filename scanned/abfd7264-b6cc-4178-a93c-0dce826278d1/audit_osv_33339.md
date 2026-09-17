# [H] tls: Use __sk_dst_get() and dst_dev_rcu() in get_netdev_for_sock().

## Summary
Severity: High
Advisory: CVE-2025-40149
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40149
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.15.199, >=5.16.0 <6.1.161, >=6.2.0 <6.6.121, >=6.7.0 <6.12.66, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: Use __sk_dst_get() and dst_dev_rcu() in get_netdev_for_sock().

get_netdev_for_sock() is called during setsockopt(),
so not under RCU.

Using sk_dst_get(sk)->dev could trigger UAF.

Let's use __sk_dst_get() and dst_dev_rcu().

Note that the only ->ndo_sk_get_lower_dev() user is
bond_sk_get_lower_dev(), which uses RCU.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/13159c7125636371543a82cb7bbae00ab36730cc
- https://git.kernel.org/stable/c/2b1bef126bbb8d0da51491357559126d567c1dee
- https://git.kernel.org/stable/c/c65f27b9c3be2269918e1cbad6d8884741f835c5
- https://git.kernel.org/stable/c/e37ca0092ddace60833790b4ad7a390408fb1be9
- https://git.kernel.org/stable/c/f09cd209359a23f88d4f3fa3d2379d057027e53c
- https://git.kernel.org/stable/c/feb474ddbf26b51f462ae2e60a12013bdcfc5407
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40149.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40149
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
