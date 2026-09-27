# [C] tunnels: do not assume transport header in iptunnel_pmtud_check_icmp()

## Summary
Severity: Critical
Advisory: CVE-2026-63992
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63992
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

tunnels: do not assume transport header in iptunnel_pmtud_check_icmp()

In some cases, iptunnel_pmtud_check_icmp() can be called while
skb transport header is not set.

This triggers an out-of-bound access, because
(typeof(skb->transport_header))~0U is 65535.

Access the icmp header based on IPv4 network header,
after making sure icmp->type is present in skb linear part.

Note that iptunnel_pmtud_check_icmpv6()) is fine.

## References
- https://git.kernel.org/stable/c/43368636c663cff6e59dde93cf4b8e43ac28eb93
- https://git.kernel.org/stable/c/509323077ef79a26ba0c60bb556e45c12c398b2d
- https://git.kernel.org/stable/c/5a92cb45e34749865d03daf8d3500f77b5f6644c
- https://git.kernel.org/stable/c/7f4f7efe7f30edd29c4988de01728bf2398217e4
- https://git.kernel.org/stable/c/a096b6e34f602950af9a2b0856cd93a5f4c276d7
- https://git.kernel.org/stable/c/c7b7ec3e69e673c0d6b57f74d21da50c485c598e
- https://git.kernel.org/stable/c/cb549df9ce4ee15c9d5b19ddab12cf2128e4313c
- https://git.kernel.org/stable/c/e917d0c69f01af2bb4fbea2b66d560a53b3ac7ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63992.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63992
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
