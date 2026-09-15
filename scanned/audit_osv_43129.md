# [H] tcp: ipv6: clamp default adverting MSS to avoid GSO_BY_FRAGS (0xFFFF)

## Summary
Severity: High
Advisory: CVE-2026-72502
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72502
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: ipv6: clamp default adverting MSS to avoid GSO_BY_FRAGS (0xFFFF)

When MTU is large, ip6_default_advmss() can return IPV6_MAXPLEN (65535).
This is interpreted by TCP as mss_clamp, allowing the MSS to reach 65535.

However, 0xFFFF is also used as a magic value GSO_BY_FRAGS in the kernel.
If a TCP packet with gso_size=0xFFFF is passed to skb_segment(), it will
be mistakenly treated as GSO_BY_FRAGS, leading to a NULL pointer
dereference because local TCP packets do not use frag_list.

Fix this by returning min(IPV6_MAXPLEN, GSO_BY_FRAGS - 1) (65534) from
ip6_default_advmss() when MTU is large.

Also update the stale comment in ip6_default_advmss() which suggested
that IPV6_MAXPLEN is returned to mean "any MSS".

## References
- https://git.kernel.org/stable/c/21f69ac1879bb970588d5e7c12a96e6542f7c1a7
- https://git.kernel.org/stable/c/2bf43d0e2e6a27d52a7d624e2d6b9116972e8a22
- https://git.kernel.org/stable/c/560b33b434e922ef97f9ff23aa2e909ef7aacd5c
- https://git.kernel.org/stable/c/572fff10819dfc359298d1f774839e76a4d96f93
- https://git.kernel.org/stable/c/8e6214a530c03e341dc1b0a846c8f2b716b3551a
- https://git.kernel.org/stable/c/a210791f33345aa87187f7d7a9f3b9b7f4a28e6d
- https://git.kernel.org/stable/c/c0db3dc2ac323b6c4b76adede3b355a9daa6dea8
- https://git.kernel.org/stable/c/d774cdbda6634a78d0f2baf201ee5a8c57f3bc0e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72502.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72502
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
