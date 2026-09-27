# [H] ipv6: mcast: extend RCU protection in igmp6_send()

## Summary
Severity: High
Advisory: CVE-2025-21759
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21759
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: mcast: extend RCU protection in igmp6_send()

igmp6_send() can be called without RTNL or RCU being held.

Extend RCU protection so that we can safely fetch the net pointer
and avoid a potential UAF.

Note that we no longer can use sock_alloc_send_skb() because
ipv6.igmp_sk uses GFP_KERNEL allocations which can sleep.

Instead use alloc_skb() and charge the net->ipv6.igmp_sk
socket under RCU protection.

## References
- https://git.kernel.org/stable/c/087c1faa594fa07a66933d750c0b2610aa1a2946
- https://git.kernel.org/stable/c/0bf8e2f3768629d437a32cb824149e6e98254381
- https://git.kernel.org/stable/c/81b25a07ebf53f9ef4ca8f3d96a8ddb94561dd5a
- https://git.kernel.org/stable/c/8e92d6a413feaf968a33f0b439ecf27404407458
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21759.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21759
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
