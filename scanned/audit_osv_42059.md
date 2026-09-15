# [H] netfilter: handle unreadable frags

## Summary
Severity: High
Advisory: CVE-2026-64414
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64414
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: handle unreadable frags

sashiko reports:
 When an skb with unreadable fragments (such as from devmem TCP, where
 skb_frags_readable(skb) returns false) is processed by the u32 module,
 skb_copy_bits() will safely return a negative error code [..]

xt_u32: bail out with hotdrop in this case.
gather_frags: return -1, just as if we had no fragment header.
nfnetlink_queue: restrict to the linear part.
nfnetlink_log: restrict to the linear part.

v2:
 - skb_zerocopy helpers don't copy readable flag, i.e. nfnetlink_queue
 is broken too
 xt_u32 shouldn't return true if hotdrop was set.

## References
- https://git.kernel.org/stable/c/3b13e7635795394705920cca1e1db7e4ca2e334b
- https://git.kernel.org/stable/c/57056be3ec12e7d9ecd20a60d4060f510e4f284c
- https://git.kernel.org/stable/c/da5b58478a9c1b85608c9e40a3b8432d071b409e
- https://git.kernel.org/stable/c/fc5bfe63bacf8a3ae307b62b34206406ca733354
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64414.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64414
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
