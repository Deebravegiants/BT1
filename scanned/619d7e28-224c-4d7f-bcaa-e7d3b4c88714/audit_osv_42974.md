# [H] netfilter: nf_conntrack_reasm: guard mac_header adjustment after IPv6 defrag

## Summary
Severity: High
Advisory: CVE-2026-72250
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72250
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_reasm: guard mac_header adjustment after IPv6 defrag

nf_ct_frag6_reasm() slides the packet head forward to drop the IPv6
fragment header and then unconditionally advances skb->mac_header:

	skb->mac_header += sizeof(struct frag_hdr);

On the NF_INET_LOCAL_OUT defrag path the skb has no link-layer header
yet, so skb->mac_header is still the "not set" sentinel (u16)~0U. Adding
sizeof(struct frag_hdr) wraps it to a small value (0xffff + 8 == 7),
after which skb_mac_header_was_set() wrongly reports a MAC header is
present and skb_mac_header() points into the headroom.

The reassembler has done this unconditional add since it was introduced;
it was harmless while mac_header was a bare pointer, but wrong once
mac_header became a u16 offset whose unset state is the ~0U sentinel
tested by skb_mac_header_was_set(). The sibling net/ipv6/reassembly.c
does the same relocation and does guard the adjustment; mirror the
guard here.

## References
- https://git.kernel.org/stable/c/00bdce2fda7e430d24cfbc96764a1b96deb31f82
- https://git.kernel.org/stable/c/2a95ec21824a8ad81ad660b12231456fc0ac9830
- https://git.kernel.org/stable/c/3b08fed5b7e0d5e3a25d73ef3ba09cd33ade16c9
- https://git.kernel.org/stable/c/53ef70a315420ed31581d38343684b3bf9a3c76d
- https://git.kernel.org/stable/c/6e8cd710ca35c576f5f2e5a396047c9ac61f75e5
- https://git.kernel.org/stable/c/a58230f3a7c4f6c3261786bc1efb72c42e68cd25
- https://git.kernel.org/stable/c/bbcdef2061b170af45702ce6b359c02c12acfc94
- https://git.kernel.org/stable/c/cd0d7bbc027b4d3329712cdcdeb4e5567ffd0d58
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72250.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72250
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
