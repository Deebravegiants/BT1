# [H] ipv6: account for fraggap on the paged allocation path

## Summary
Severity: High
Advisory: CVE-2026-53362
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2026-53362
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: account for fraggap on the paged allocation path

In __ip6_append_data(), when the paged-allocation branch is taken
(MSG_MORE / NETIF_F_SG / large fraglen), alloclen and pagedlen are
computed as

	alloclen = fragheaderlen + transhdrlen;
	pagedlen = datalen - transhdrlen;

datalen already includes fraggap (datalen = length + fraggap). When
fraggap is non-zero, this is not the first skb and transhdrlen is zero.
The fraggap bytes carried over from the previous skb are copied just past
the fragment headers in the new skb's linear area. The linear area is
therefore undersized by fraggap bytes while pagedlen is overstated by the
same amount, and the copy writes past skb->end into the trailing
skb_shared_info.

An unprivileged user can trigger this via a UDPv6 socket using
MSG_MORE together with MSG_SPLICE_PAGES.

The bad accounting was introduced by commit 773ba4fe9104 ("ipv6:
avoid partial copy for zc"). Before commit ce650a166335 ("udp6: Fix
__ip6_append_data()'s handling of MSG_SPLICE_PAGES"), the negative
copy value caused -EINVAL to be returned. That later commit allowed
MSG_SPLICE_PAGES to proceed in this case, making the corruption
triggerable.

The non-paged branch sets alloclen to fraglen, which already accounts
for fraggap because datalen does. Bring the paged branch in line by
adding fraggap to alloclen and subtracting it from pagedlen.

After this adjustment, copy no longer collapses to -fraggap on the
paged path, so remove the stale comment describing that old arithmetic.
Since a negative copy is no longer expected for a valid MSG_SPLICE_PAGES
case, remove the MSG_SPLICE_PAGES exception from the negative copy check.

## References
- https://git.kernel.org/stable/c/14200d435af9a9eeb444f529fc2f689a236b7962
- https://git.kernel.org/stable/c/46f201f8b4c39633a1fa3dc12459f506d470993d
- https://git.kernel.org/stable/c/6374fb9edf72c67a118a2c214a0dddd04c921e0a
- https://git.kernel.org/stable/c/65fb14cbebb0cd0eff903a22d33537ddc8b95769
- https://git.kernel.org/stable/c/736b380e28d0480c7bc3e022f1950f31fe53a7c5
- https://git.kernel.org/stable/c/e9eacf19281ea2498b36291b56c9606118c2d74e
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-53362
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53362.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53362
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
