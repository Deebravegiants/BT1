# [H] ipv6: ioam: add NULL check for idev in ipv6_hop_ioam()

## Summary
Severity: High
Advisory: CVE-2026-64116
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64116
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: ioam: add NULL check for idev in ipv6_hop_ioam()

Reported by Sashiko:

The function ipv6_hop_ioam() accesses
__in6_dev_get(skb->dev)->cnf.ioam6_enabled without validating the returned
idev pointer. Because addrconf_ifdown() can concurrently clear dev->ip6_ptr
via RCU, __in6_dev_get() can return NULL during interface teardown, which
could cause a NULL pointer dereference when processing an IOAM Hop-by-Hop
option.

Let's add a check and use SKB_DROP_REASON_IPV6DISABLED accordingly.

## References
- https://git.kernel.org/stable/c/09cbfd4b81ae90963dadb1de99b63b702e73290a
- https://git.kernel.org/stable/c/1dca7e491f070ac49b3d934f16ee953a53b37f38
- https://git.kernel.org/stable/c/902daac307eb7e1955ce05b071950f3cba88c963
- https://git.kernel.org/stable/c/abdd03229414b5a52943b65a60f34b84cea5ac59
- https://git.kernel.org/stable/c/c7e8971abd70e9d022f1c251ba2508f8dc7f2db8
- https://git.kernel.org/stable/c/cf75eb6617042c8cff6112daeed7791809fc9dd2
- https://git.kernel.org/stable/c/d4ea0dfd75011b78cebf3808f98ac4c4f51a6fb9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64116.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64116
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
